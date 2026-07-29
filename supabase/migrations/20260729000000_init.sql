-- Restaurant Voice SaaS schema + RLS
create extension if not exists "pgcrypto";

create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text not null unique,
  stripe_customer_id text,
  plan text not null default 'free',
  status text not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists memberships (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  user_id uuid not null,
  role text not null check (role in ('owner','admin','staff','viewer')),
  created_at timestamptz not null default now(),
  unique (org_id, user_id)
);

create table if not exists restaurants (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  name text not null,
  timezone text not null default 'America/Chicago',
  phone_e164 text,
  address_json jsonb not null default '{}'::jsonb,
  transfer_number_e164 text,
  sms_from_number text,
  hours_json jsonb not null default '{}'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now()
);

create table if not exists voice_agents (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null unique references restaurants(id) on delete cascade,
  twilio_number_sid text,
  twilio_phone_e164 text unique,
  voice_id text not null,
  language text not null default 'en',
  system_prompt text not null default '',
  greeting text not null default 'Thanks for calling. How can I help you today?',
  transfer_policy_json jsonb not null default '{}'::jsonb,
  active boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists menus (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references restaurants(id) on delete cascade,
  title text not null,
  version int not null default 1,
  published_at timestamptz
);

create table if not exists menu_items (
  id uuid primary key default gen_random_uuid(),
  menu_id uuid not null references menus(id) on delete cascade,
  name text not null,
  description text not null default '',
  price_cents int not null,
  category text not null default 'general',
  allergens_json jsonb not null default '[]'::jsonb,
  available boolean not null default true,
  embedding jsonb
);

create table if not exists faqs (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references restaurants(id) on delete cascade,
  question text not null,
  answer text not null,
  tags text[] not null default '{}',
  active boolean not null default true,
  embedding jsonb
);

create table if not exists reservations (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references restaurants(id) on delete cascade,
  guest_name text not null,
  guest_phone text not null,
  party_size int not null check (party_size between 1 and 20),
  starts_at timestamptz not null,
  status text not null check (status in ('pending','confirmed','cancelled','no_show')),
  source text not null default 'voice',
  notes text,
  confirmation_code text not null
);
create index if not exists reservations_restaurant_starts on reservations(restaurant_id, starts_at);

create table if not exists calls (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references restaurants(id) on delete cascade,
  twilio_call_sid text not null unique,
  from_number text,
  to_number text,
  direction text not null default 'inbound',
  started_at timestamptz not null default now(),
  ended_at timestamptz,
  duration_sec int,
  outcome text,
  recording_url text,
  recording_storage_path text,
  recording_purged_at timestamptz,
  cost_estimate_cents int
);
create index if not exists calls_restaurant_started on calls(restaurant_id, started_at desc);

create table if not exists call_turns (
  id uuid primary key default gen_random_uuid(),
  call_id uuid not null references calls(id) on delete cascade,
  role text not null,
  content text not null,
  tool_name text,
  latency_ms int,
  created_at timestamptz not null default now()
);

create table if not exists sms_messages (
  id uuid primary key default gen_random_uuid(),
  restaurant_id uuid not null references restaurants(id) on delete cascade,
  call_id uuid references calls(id) on delete set null,
  to_number text not null,
  body text not null,
  status text,
  twilio_sid text,
  direction text default 'outbound',
  created_at timestamptz not null default now()
);

create table if not exists billing_subscriptions (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  stripe_subscription_id text,
  price_id text,
  status text,
  current_period_end timestamptz,
  minutes_included int default 500,
  minutes_used int default 0
);

create table if not exists usage_events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  restaurant_id uuid references restaurants(id) on delete set null,
  call_id uuid references calls(id) on delete set null,
  metric text not null,
  quantity numeric not null,
  created_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  actor_user_id uuid,
  action text not null,
  entity text not null,
  entity_id text not null,
  meta_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- RLS
alter table organizations enable row level security;
alter table memberships enable row level security;
alter table restaurants enable row level security;
alter table voice_agents enable row level security;
alter table menus enable row level security;
alter table menu_items enable row level security;
alter table faqs enable row level security;
alter table reservations enable row level security;
alter table calls enable row level security;
alter table call_turns enable row level security;
alter table sms_messages enable row level security;
alter table billing_subscriptions enable row level security;
alter table usage_events enable row level security;
alter table audit_logs enable row level security;

create or replace function public.user_org_ids()
returns setof uuid
language sql
stable
security definer
set search_path = public
as $$
  select org_id from memberships where user_id = auth.uid();
$$;

create policy org_member_select on organizations for select using (id in (select public.user_org_ids()));
create policy membership_select on memberships for select using (org_id in (select public.user_org_ids()));
create policy restaurants_all on restaurants for all using (org_id in (select public.user_org_ids()));
create policy voice_agents_all on voice_agents for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy menus_all on menus for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy menu_items_all on menu_items for all using (
  menu_id in (select m.id from menus m join restaurants r on r.id = m.restaurant_id where r.org_id in (select public.user_org_ids()))
);
create policy faqs_all on faqs for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy reservations_all on reservations for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy calls_all on calls for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy call_turns_all on call_turns for all using (
  call_id in (select c.id from calls c join restaurants r on r.id = c.restaurant_id where r.org_id in (select public.user_org_ids()))
);
create policy sms_all on sms_messages for all using (
  restaurant_id in (select id from restaurants where org_id in (select public.user_org_ids()))
);
create policy billing_all on billing_subscriptions for all using (org_id in (select public.user_org_ids()));
create policy usage_all on usage_events for all using (org_id in (select public.user_org_ids()));
create policy audit_select on audit_logs for select using (org_id in (select public.user_org_ids()));
