-- Create table for Vinted items scraped from a public profile
create table if not exists public.items (
  id bigserial primary key,
  sku text,
  title text not null,
  brand text,
  size text,
  price_eur double precision,
  cost_eur double precision,
  margin_eur double precision,
  status text default 'en_stock',
  image_url text,
  item_url text unique,
  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_items_status on public.items(status);
create index if not exists idx_items_created_at on public.items(created_at desc);

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_set_updated_at on public.items;
create trigger trg_set_updated_at
before update on public.items
for each row execute function public.set_updated_at();
