-- ============================================================
-- MECATECH DATABASE - Supabase Setup
-- Run this entire file in Supabase SQL Editor
-- ============================================================

-- ── 1. CREATE TABLES ─────────────────────────────────────────

create table if not exists clientes (
  id bigint generated always as identity primary key,
  nombre text not null,
  password text default '0000'
);

create table if not exists pedidos (
  id bigint generated always as identity primary key,
  "Fecha" text,
  "Numero_Pedido" text,
  "Cliente" text,
  "Codigo_Pieza" text,
  "Nombre_Pieza" text,
  "Precio_Unitario" float,
  "Cantidad" int,
  "Precio_Total" float,
  "Estado_Pedido" text,
  "Comentarios" text,
  "EstadoVisualizacion" text default 'Visible'
);

create table if not exists pagos (
  id bigint generated always as identity primary key,
  "Fecha" text,
  "Numero_Pago" text,
  "Cliente" text,
  "Numero_Pedido_Ref" text,
  "Codigo_Pieza_Ref" text,
  "Monto_Pago" float,
  "Comentarios" text,
  "EstadoVisualizacion" text default 'Visible'
);

-- ── 2. INSERT CLIENTES (39 clients) ──────────────────────────

insert into clientes (nombre, password) values
('Dante Covino', '0000'),
('Claudio Makoveck', '0000'),
('Marcelo Iglesias', '0000'),
('Rodrigo Diaz Perez', '0000'),
('Raul Alfajeme', '0000'),
('Luis Hererria', '0000'),
('Marcelo Fileni', '0000'),
('Alejandro Barlaro', '0000'),
('Esteban Molina', '0000'),
('Alejandro Fonfreda', '0000'),
('Adrian Paiz', '0000'),
('Diego Canals', '0000'),
('Ezequiel Laus', '0000'),
('Santiago Subiat', '0000'),
('Cristian Mazzini', '0000'),
('Brother', '0000'),
('Jose Labriola', '0000'),
('Tiburon', '0000'),
('Juan carlos Torres', '0000'),
('Leandro Robledo', '0000'),
('Mara', '0000'),
('Javier Diaz', '0000'),
('Pelado Zabbataro', '0000'),
('Sebastian Corti', '0000'),
('Christian Sanzio', '0000'),
('Reinaldo Rubio', '0000'),
('Marcos Coronel', '0000'),
('Marcelo Haeberli', '0000'),
('David Cuello', '0000'),
('TIO mdq', '0000'),
('Rastelli', '0000'),
('Daniel Azuri', '0000'),
('Gustavo Rainone', '0000'),
('Jorge paganelli', '0000'),
('Diego Lucero', '0000'),
('VARIOS STOCK', '0000'),
('Matias Garcia', '0000'),
('Diego Boim', '0000'),
('Sergio Garcia', '1234');

-- ── 3. INSERT PEDIDOS ─────────────────────────────────────────

insert into pedidos ("Fecha", "Numero_Pedido", "Cliente", "Codigo_Pieza", "Nombre_Pieza", "Precio_Unitario", "Cantidad", "Precio_Total", "Estado_Pedido", "Comentarios", "EstadoVisualizacion") values
('2025-11-24 16:22:42', 'PED001', 'Marcelo Iglesias', '1000-38', 'pastilla de freno ', 37.21, 1, 37.21, 'PENDIENTE', '', 'Visible'),
('2025-11-24 16:23:14', 'PED002', 'Marcelo Iglesias', '1000-40', 'disco de freno viejo', 36.84, 1, 36.84, 'PAGADO', '', 'Visible');

-- ── 4. INSERT PAGOS ───────────────────────────────────────────

insert into pagos ("Fecha", "Numero_Pago", "Cliente", "Numero_Pedido_Ref", "Codigo_Pieza_Ref", "Monto_Pago", "Comentarios", "EstadoVisualizacion") values
('2025-11-24 16:22:50', 'PAG001', 'Marcelo Iglesias', 'PED001', '1000-38', 37.21, '', 'Visible'),
('2025-11-24 16:23:14', 'PAG002', 'Marcelo Iglesias', 'PED002', '1000-40', 36.84, 'Pago inmediato para pedido PED002', 'Visible');

-- ── 5. DISABLE Row Level Security (allow app to read/write) ──

alter table clientes enable row level security;
alter table pedidos enable row level security;
alter table pagos enable row level security;

create policy "Allow all" on clientes for all using (true) with check (true);
create policy "Allow all" on pedidos for all using (true) with check (true);
create policy "Allow all" on pagos for all using (true) with check (true);
