insert into organizations (id, name, slug, plan, status)
values ('11111111-1111-1111-1111-111111111111', 'Demo Bistro Org', 'demo-bistro', 'pro', 'active')
on conflict do nothing;

insert into memberships (id, org_id, user_id, role)
values ('22222222-2222-2222-2222-222222222222', '11111111-1111-1111-1111-111111111111', '33333333-3333-3333-3333-333333333333', 'owner')
on conflict do nothing;

insert into restaurants (id, org_id, name, timezone, transfer_number_e164, hours_json, status, phone_e164, sms_from_number)
values (
  '44444444-4444-4444-4444-444444444444',
  '11111111-1111-1111-1111-111111111111',
  'Demo Bistro',
  'America/Chicago',
  '+15555550999',
  '{"mon-sun":"11:00-22:00"}'::jsonb,
  'ready',
  '+15555550100',
  '+15555550100'
) on conflict do nothing;

insert into voice_agents (id, restaurant_id, twilio_phone_e164, voice_id, greeting, active)
values (
  '55555555-5555-5555-5555-555555555555',
  '44444444-4444-4444-4444-444444444444',
  '+15555550100',
  '21m00Tcm4TlvDq8ikWAM',
  'Thanks for calling Demo Bistro!',
  true
) on conflict do nothing;

insert into menus (id, restaurant_id, title, version, published_at)
values ('66666666-6666-6666-6666-666666666666', '44444444-4444-4444-4444-444444444444', 'Main Menu', 1, now())
on conflict do nothing;

insert into menu_items (id, menu_id, name, description, price_cents, category)
values
  ('77777777-7777-7777-7777-777777777771', '66666666-6666-6666-6666-666666666666', 'Margherita Pizza', 'Tomato, mozzarella, basil', 1400, 'pizza'),
  ('77777777-7777-7777-7777-777777777772', '66666666-6666-6666-6666-666666666666', 'Caesar Salad', 'Romaine, parmesan, croutons', 900, 'salads')
on conflict do nothing;

insert into faqs (id, restaurant_id, question, answer, tags)
values
  ('88888888-8888-8888-8888-888888888881', '44444444-4444-4444-4444-444444444444', 'Do you have parking?', 'Street parking and a lot behind the restaurant.', array['parking']),
  ('88888888-8888-8888-8888-888888888882', '44444444-4444-4444-4444-444444444444', 'Are you kid friendly?', 'Yes, we have a kids menu and high chairs.', array['kids'])
on conflict do nothing;
