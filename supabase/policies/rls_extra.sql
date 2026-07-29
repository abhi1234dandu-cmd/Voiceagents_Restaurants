-- Extra RLS policies (apply after migration). Drop first for idempotency.

drop policy if exists org_member_insert on organizations;
create policy org_member_insert on organizations
  for insert with check (true);

drop policy if exists membership_insert on memberships;
create policy membership_insert on memberships
  for insert with check (org_id in (select public.user_org_ids()) or user_id = auth.uid());

drop policy if exists membership_update on memberships;
create policy membership_update on memberships
  for update using (
    org_id in (
      select m.org_id from memberships m
      where m.user_id = auth.uid() and m.role in ('owner', 'admin')
    )
  );

drop policy if exists audit_insert on audit_logs;
create policy audit_insert on audit_logs
  for insert with check (org_id in (select public.user_org_ids()));
