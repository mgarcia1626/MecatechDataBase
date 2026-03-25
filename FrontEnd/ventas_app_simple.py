"""
Aplicación Streamlit para Gestión de Ventas y Pagos - MecatechDataBase.

Interfaz web simplificada para registrar pedidos, pagos y pagos inmediatos.
Backend: Supabase (cuando SUPABASE_URL y SUPABASE_KEY están configurados)
         CSV/JSON local (fallback para desarrollo local)
"""

import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime
import csv
import json

# Configurar paths para importación
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent
base_project_dir = parent_dir  # Relative path — works both locally and on Railway

# Agregar paths al sistema
paths_to_add = [
    str(parent_dir),
    str(base_project_dir),
    str(base_project_dir / "Functions"),
    str(base_project_dir / "Functions" / "SalesManager")
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.append(path)

# ── Supabase connection ───────────────────────────────────────────────────────
_supabase_error = ""
try:
    from supabase import create_client
    _SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    _SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    if _SUPABASE_URL and _SUPABASE_KEY:
        _supabase = create_client(_SUPABASE_URL, _SUPABASE_KEY)
        USE_SUPABASE = True
    else:
        _supabase = None
        USE_SUPABASE = False
        _supabase_error = f"Variables vacías — URL={repr(_SUPABASE_URL[:20] if _SUPABASE_URL else '')}, KEY={repr(_SUPABASE_KEY[:10] if _SUPABASE_KEY else '')}"
except Exception as e:
    _supabase = None
    USE_SUPABASE = False
    _supabase_error = str(e)
# ─────────────────────────────────────────────────────────────────────────────


class SalesManager:
    def __init__(self):
        self.base_dir = base_project_dir
        # Local file paths (used as fallback when Supabase is not configured)
        self.pedidos_path = self.base_dir / "DataBase" / "Generated" / "pedidos.csv"
        self.pagos_path = self.base_dir / "DataBase" / "Generated" / "pagos.csv"
        self.clients_path = self.base_dir / "DataBase" / "Generated" / "clientes.json"
        self.products_path = self.base_dir / "DataBase" / "Generated" / "mecatech_database.json"

        if not USE_SUPABASE:
            self.pedidos_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_pedidos_csv()
            self._init_pagos_csv()

        self._load_clients()
        self._load_products()

    # ── Init CSV (local fallback only) ────────────────────────────────────────
    def _init_pedidos_csv(self):
        if not self.pedidos_path.exists():
            headers = ['Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza',
                       'Precio_Unitario', 'Cantidad', 'Precio_Total', 'Estado_Pedido',
                       'Comentarios', 'EstadoVisualizacion']
            with open(self.pedidos_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(headers)

    def _init_pagos_csv(self):
        if not self.pagos_path.exists():
            headers = ['Fecha', 'Numero_Pago', 'Cliente', 'Numero_Pedido_Ref',
                       'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios', 'EstadoVisualizacion']
            with open(self.pagos_path, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(headers)

    # ── Load clients ──────────────────────────────────────────────────────────
    def _load_clients(self):
        if USE_SUPABASE:
            try:
                rows = _supabase.table("clientes").select("*").execute().data
                self.clients_data = {"clientes": [{"nombre": r["nombre"], "password": r.get("password", "0000")} for r in rows]}
            except Exception as e:
                st.warning(f"⚠️ Error cargando clientes desde Supabase: {e}")
                self.clients_data = {"clientes": []}
        else:
            try:
                if self.clients_path.exists():
                    with open(self.clients_path, 'r', encoding='utf-8') as f:
                        self.clients_data = json.load(f)
                else:
                    self.clients_data = {"clientes": []}
            except:
                self.clients_data = {"clientes": []}

    def _load_products(self):
        try:
            if self.products_path.exists():
                with open(self.products_path, 'r', encoding='utf-8') as f:
                    self.products_data = json.load(f)
            else:
                self.products_data = {}
        except:
            self.products_data = {}

    # ── Client helpers ────────────────────────────────────────────────────────
    def get_client_names(self):
        return [client["nombre"] for client in self.clients_data["clientes"]]

    # ── Product helpers ───────────────────────────────────────────────────────
    def search_products_by_name(self, search_term):
        results = []
        if not search_term:
            return results
        search_term = search_term.lower()
        for code, product in self.products_data.items():
            name_english = product.get('name', '').lower()
            name_spanish = product.get('espanol', '').lower() if product.get('espanol') else ''
            if search_term in name_english or search_term in name_spanish or search_term in code.lower():
                results.append((code, product.get('espanol', ''), product.get('name', '')))
        return results[:20]

    def get_product_sell_price(self, code):
        product = self.products_data.get(code)
        if not product:
            return 0.0
        return float(product.get('ARG', {}).get('Sell_price', 0.0))

    # ── Number generators ─────────────────────────────────────────────────────
    def generate_pedido_number(self):
        try:
            df = self.load_pedidos()
            if df.empty:
                return "PED001"
            nums = df['Numero_Pedido'].str.extract(r'PED(\d+)').dropna().astype(int)
            return f"PED{nums[0].max() + 1:03d}" if not nums.empty else "PED001"
        except:
            return "PED001"

    def generate_pago_number(self):
        try:
            df = self.load_pagos()
            if df.empty:
                return "PAG001"
            nums = df['Numero_Pago'].str.extract(r'PAG(\d+)').dropna().astype(int)
            return f"PAG{nums[0].max() + 1:03d}" if not nums.empty else "PAG001"
        except:
            return "PAG001"

    # ── Load data → DataFrame ─────────────────────────────────────────────────
    def load_pedidos(self):
        if USE_SUPABASE:
            try:
                rows = _supabase.table("pedidos").select("*").execute().data
                return pd.DataFrame(rows) if rows else pd.DataFrame()
            except Exception as e:
                st.warning(f"⚠️ Error cargando pedidos: {e}")
                return pd.DataFrame()
        else:
            try:
                return pd.read_csv(self.pedidos_path) if self.pedidos_path.exists() else pd.DataFrame()
            except:
                return pd.DataFrame()

    def load_pagos(self):
        if USE_SUPABASE:
            try:
                rows = _supabase.table("pagos").select("*").execute().data
                return pd.DataFrame(rows) if rows else pd.DataFrame()
            except Exception as e:
                st.warning(f"⚠️ Error cargando pagos: {e}")
                return pd.DataFrame()
        else:
            try:
                return pd.read_csv(self.pagos_path) if self.pagos_path.exists() else pd.DataFrame()
            except:
                return pd.DataFrame()

    # ── Add records ───────────────────────────────────────────────────────────
    def add_pedido(self, cliente, codigo_pieza, precio_venta=None, comentarios="", numero_pedido=None):
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if numero_pedido is None:
                numero_pedido = self.generate_pedido_number()
            if precio_venta is None:
                precio_venta = self.get_product_sell_price(codigo_pieza)
            product_name = (self.products_data.get(codigo_pieza, {}).get('espanol') or
                            self.products_data.get(codigo_pieza, {}).get('name', 'Producto no encontrado'))
            record = {
                "Fecha": fecha_actual, "Numero_Pedido": numero_pedido, "Cliente": cliente,
                "Codigo_Pieza": codigo_pieza, "Nombre_Pieza": product_name,
                "Precio_Unitario": precio_venta, "Cantidad": 1, "Precio_Total": precio_venta,
                "Estado_Pedido": "PENDIENTE", "Comentarios": comentarios, "EstadoVisualizacion": "Visible"
            }
            if USE_SUPABASE:
                _supabase.table("pedidos").insert(record).execute()
            else:
                with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(list(record.values()))
            return True, numero_pedido
        except Exception as e:
            st.error(f"Error al agregar pedido: {e}")
            return False, None

    def add_pedido_multiple(self, cliente, productos_list, comentarios=""):
        try:
            if not productos_list:
                return False, None
            numero_pedido = self.generate_pedido_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            records = []
            for item in productos_list:
                product_name = (self.products_data.get(item['codigo'], {}).get('espanol') or
                                self.products_data.get(item['codigo'], {}).get('name', 'Producto no encontrado'))
                records.append({
                    "Fecha": fecha_actual, "Numero_Pedido": numero_pedido, "Cliente": cliente,
                    "Codigo_Pieza": item['codigo'], "Nombre_Pieza": product_name,
                    "Precio_Unitario": item['precio_unitario'], "Cantidad": item['cantidad'],
                    "Precio_Total": item['subtotal'], "Estado_Pedido": "PENDIENTE",
                    "Comentarios": comentarios, "EstadoVisualizacion": "Visible"
                })
            if USE_SUPABASE:
                _supabase.table("pedidos").insert(records).execute()
            else:
                with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                    w = csv.writer(f)
                    for r in records:
                        w.writerow(list(r.values()))
            return True, numero_pedido
        except Exception as e:
            st.error(f"Error al agregar pedido múltiple: {e}")
            return False, None

    def add_pago(self, cliente, monto_pago, numero_pedido_ref="", codigo_pieza_ref="", comentarios=""):
        try:
            numero_pago = self.generate_pago_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "Fecha": fecha_actual, "Numero_Pago": numero_pago, "Cliente": cliente,
                "Numero_Pedido_Ref": numero_pedido_ref, "Codigo_Pieza_Ref": codigo_pieza_ref,
                "Monto_Pago": monto_pago, "Comentarios": comentarios, "EstadoVisualizacion": "Visible"
            }
            if USE_SUPABASE:
                _supabase.table("pagos").insert(record).execute()
            else:
                with open(self.pagos_path, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(list(record.values()))
            return True, numero_pago
        except Exception as e:
            st.error(f"Error al agregar pago: {e}")
            return False, None

    def add_pago_inmediato(self, cliente, codigo_pieza, precio_venta, comentarios=""):
        try:
            success_pedido, numero_pedido = self.add_pedido(cliente, codigo_pieza, precio_venta, comentarios)
            if success_pedido:
                comentarios_pago = f"Pago inmediato para pedido {numero_pedido}"
                if comentarios:
                    comentarios_pago += f" - {comentarios}"
                success_pago, numero_pago = self.add_pago(cliente, precio_venta, numero_pedido, codigo_pieza, comentarios_pago)
                if success_pago:
                    return True, numero_pedido, numero_pago
            return False, None, None
        except Exception as e:
            st.error(f"Error en pago inmediato: {e}")
            return False, None, None

    # ── Statistics ────────────────────────────────────────────────────────────
    def get_statistics(self):
        df_pedidos = self.load_pedidos()
        df_pagos = self.load_pagos()
        total_sales = df_pedidos['Precio_Total'].sum() if not df_pedidos.empty else 0.0
        total_payments = df_pagos['Monto_Pago'].sum() if not df_pagos.empty else 0.0
        unique_clients = len(
            (set(df_pedidos['Cliente'].unique()) if not df_pedidos.empty else set()) |
            (set(df_pagos['Cliente'].unique()) if not df_pagos.empty else set())
        )
        return {
            "total_transactions": len(df_pedidos) + len(df_pagos),
            "total_sales": round(total_sales, 2),
            "total_payments": round(total_payments, 2),
            "net_balance": round(total_sales - total_payments, 2),
            "unique_clients": unique_clients,
            "unique_products": len(df_pedidos['Codigo_Pieza'].unique()) if not df_pedidos.empty else 0,
        }

    # ── Client views ──────────────────────────────────────────────────────────
    def get_client_pedidos(self, cliente, incluir_ocultos=False):
        if USE_SUPABASE:
            try:
                q = _supabase.table("pedidos").select("*").eq("Cliente", cliente)
                if not incluir_ocultos:
                    q = q.eq("EstadoVisualizacion", "Visible")
                rows = q.execute().data
                df = pd.DataFrame(rows) if rows else pd.DataFrame()
                return df.sort_values('Fecha', ascending=False) if not df.empty else df
            except Exception as e:
                st.warning(f"⚠️ Error: {e}")
                return pd.DataFrame()
        else:
            df = self.load_pedidos()
            if df.empty:
                return df
            df = df[df['Cliente'] == cliente]
            if not incluir_ocultos and 'EstadoVisualizacion' in df.columns:
                df = df[df['EstadoVisualizacion'] == 'Visible']
            return df.sort_values('Fecha', ascending=False)

    def get_client_pagos(self, cliente, incluir_ocultos=False):
        if USE_SUPABASE:
            try:
                q = _supabase.table("pagos").select("*").eq("Cliente", cliente)
                if not incluir_ocultos:
                    q = q.eq("EstadoVisualizacion", "Visible")
                rows = q.execute().data
                df = pd.DataFrame(rows) if rows else pd.DataFrame()
                return df.sort_values('Fecha', ascending=False) if not df.empty else df
            except Exception as e:
                st.warning(f"⚠️ Error: {e}")
                return pd.DataFrame()
        else:
            df = self.load_pagos()
            if df.empty:
                return df
            df = df[df['Cliente'] == cliente]
            if not incluir_ocultos and 'EstadoVisualizacion' in df.columns:
                df = df[df['EstadoVisualizacion'] == 'Visible']
            return df.sort_values('Fecha', ascending=False)

    def get_client_balance(self, cliente):
        df_pedidos = self.get_client_pedidos(cliente)
        df_pagos = self.get_client_pagos(cliente)
        total_deuda = df_pedidos['Precio_Total'].sum() if not df_pedidos.empty else 0.0
        total_pagos = df_pagos['Monto_Pago'].sum() if not df_pagos.empty else 0.0
        return {
            "total_deuda": round(total_deuda, 2),
            "total_pagos": round(total_pagos, 2),
            "balance": round(total_deuda - total_pagos, 2),
        }

    # ── Hide / Delete ─────────────────────────────────────────────────────────
    def ocultar_pedido(self, numero_pedido):
        try:
            if USE_SUPABASE:
                _supabase.table("pedidos").update({"EstadoVisualizacion": "Oculto"}).eq("Numero_Pedido", numero_pedido).execute()
            else:
                df = self.load_pedidos()
                df.loc[df['Numero_Pedido'] == numero_pedido, 'EstadoVisualizacion'] = 'Oculto'
                df.to_csv(self.pedidos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error ocultando pedido: {e}")
            return False

    def ocultar_pago(self, numero_pago):
        try:
            if USE_SUPABASE:
                _supabase.table("pagos").update({"EstadoVisualizacion": "Oculto"}).eq("Numero_Pago", numero_pago).execute()
            else:
                df = self.load_pagos()
                df.loc[df['Numero_Pago'] == numero_pago, 'EstadoVisualizacion'] = 'Oculto'
                df.to_csv(self.pagos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error ocultando pago: {e}")
            return False

    def eliminar_pedido(self, numero_pedido):
        try:
            if USE_SUPABASE:
                _supabase.table("pedidos").delete().eq("Numero_Pedido", numero_pedido).execute()
            else:
                df = self.load_pedidos()
                df = df[df['Numero_Pedido'] != numero_pedido]
                df.to_csv(self.pedidos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error eliminando pedido: {e}")
            return False
    
    def eliminar_pago(self, numero_pago):
        try:
            if USE_SUPABASE:
                _supabase.table("pagos").delete().eq("Numero_Pago", numero_pago).execute()
            else:
                df = self.load_pagos()
                df = df[df['Numero_Pago'] != numero_pago]
                df.to_csv(self.pagos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error eliminando pago: {e}")
            return False

    def mostrar_pedido(self, numero_pedido):
        try:
            if USE_SUPABASE:
                _supabase.table("pedidos").update({"EstadoVisualizacion": "Visible"}).eq("Numero_Pedido", numero_pedido).execute()
            else:
                df = self.load_pedidos()
                df.loc[df['Numero_Pedido'] == numero_pedido, 'EstadoVisualizacion'] = 'Visible'
                df.to_csv(self.pedidos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error mostrando pedido: {e}")
            return False

    def mostrar_pago(self, numero_pago):
        try:
            if USE_SUPABASE:
                _supabase.table("pagos").update({"EstadoVisualizacion": "Visible"}).eq("Numero_Pago", numero_pago).execute()
            else:
                df = self.load_pagos()
                df.loc[df['Numero_Pago'] == numero_pago, 'EstadoVisualizacion'] = 'Visible'
                df.to_csv(self.pagos_path, index=False)
            return True
        except Exception as e:
            print(f"❌ Error mostrando pago: {e}")
            return False

    def agregar_cliente(self, nombre, password="0000"):
        try:
            nombres_existentes = [c["nombre"].lower() for c in self.clients_data["clientes"]]
            if nombre.lower() in nombres_existentes:
                return False, "El cliente ya existe"
            if USE_SUPABASE:
                _supabase.table("clientes").insert({"nombre": nombre, "password": password}).execute()
            else:
                self.clients_data["clientes"].append({"nombre": nombre, "password": password})
                with open(self.clients_path, 'w', encoding='utf-8') as f:
                    json.dump(self.clients_data, f, indent=2, ensure_ascii=False)
            self._load_clients()
            return True, f"Cliente '{nombre}' agregado exitosamente"
        except Exception as e:
            return False, str(e)

    def agregar_producto(self, codigo, nombre_espanol="", final_cost_usa=0.0, peso=None, precio_venta=0.0, nombre_ingles=""):
        try:
            if codigo in self.products_data:
                return False, f"El producto con código '{codigo}' ya existe"
            nuevo_producto = {
                "name": nombre_ingles or nombre_espanol,
                "espanol": nombre_espanol if nombre_espanol else None,
                "qty_for_bag": 1,
                "dealer_price": 0.0,
                "consumer_price": 0.0,
                "total_in_usa": 0.0,
                "cost_in_usa_usd": 0.0,
                "final_cost_usa": final_cost_usa,
                "ARG": {
                    "weight": peso,
                    "shipping_cost": 5.0,
                    "Costo_In_Arg": 0.0,
                    "Ref_Price": 0.0,
                    "Sell_price": precio_venta,
                    "Reference_percent": 0.0
                }
            }
            self.products_data[codigo] = nuevo_producto
            with open(self.products_path, 'w', encoding='utf-8') as f:
                json.dump(self.products_data, f, indent=2, ensure_ascii=False)
            return True, f"Producto '{codigo}' agregado exitosamente"
        except Exception as e:
            return False, str(e)

    def obtener_estadisticas_administracion(self):
        try:
            total_clientes = len(self.get_client_names())
            total_productos = len(self.products_data)
            productos_con_espanol = sum(1 for p in self.products_data.values() if p.get('espanol'))
            return {
                "total_clientes": total_clientes,
                "total_productos": total_productos,
                "productos_con_espanol": productos_con_espanol,
                "productos_sin_espanol": total_productos - productos_con_espanol,
            }
        except:
            return {"total_clientes": 0, "total_productos": 0, "productos_con_espanol": 0, "productos_sin_espanol": 0}


def init_session_state():
    """Inicializa variables del estado de sesión."""
    if 'sales_manager' not in st.session_state:
        st.session_state.sales_manager = SalesManager()
    
    if 'carrito_pedido' not in st.session_state:
        st.session_state.carrito_pedido = []
    
    if 'total_pedido' not in st.session_state:
        st.session_state.total_pedido = 0.0
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
        
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = None

def search_products(search_term):
    """Búsqueda de productos y almacenamiento en session state."""
    if search_term:
        results = st.session_state.sales_manager.search_products_by_name(search_term)
        st.session_state.search_results = results
        if st.session_state.selected_product:
            st.session_state.selected_product = None

def add_to_cart(codigo, nombre, precio_unitario, cantidad=1):
    """Agrega un producto al carrito."""
    # Verificar si ya existe en el carrito
    for item in st.session_state.carrito_pedido:
        if item['codigo'] == codigo:
            item['cantidad'] += cantidad
            item['subtotal'] = item['precio_unitario'] * item['cantidad']
            update_total()
            return
    
    # Si no existe, agregarlo
    subtotal = precio_unitario * cantidad
    item = {
        'codigo': codigo,
        'nombre': nombre,
        'precio_unitario': precio_unitario,
        'cantidad': cantidad,
        'subtotal': subtotal
    }
    st.session_state.carrito_pedido.append(item)
    update_total()

def remove_from_cart(index):
    """Remueve un producto del carrito."""
    if 0 <= index < len(st.session_state.carrito_pedido):
        del st.session_state.carrito_pedido[index]
        update_total()

def clear_cart():
    """Limpia todo el carrito."""
    st.session_state.carrito_pedido = []
    st.session_state.total_pedido = 0.0

def update_total():
    """Actualiza el total del pedido."""
    total = sum(item['subtotal'] for item in st.session_state.carrito_pedido)
    st.session_state.total_pedido = total

def main():
    st.set_page_config(
        page_title="Ventas y Pagos - MecatechDataBase",
        page_icon="🏪",
        layout="wide"
    )
    
    # Inicializar estado
    init_session_state()
    
    st.title("🏪 Sistema de Pedidos y Pagos")
    st.markdown("---")
    
    # Sidebar con estadísticas
    with st.sidebar:
        if USE_SUPABASE:
            st.success("🟢 Supabase conectado")
        else:
            st.warning("🟡 Modo local (CSV/JSON)")
            if _supabase_error:
                st.error(f"Error Supabase: {_supabase_error}")
        st.subheader("📊 Estadísticas Generales")
        stats = st.session_state.sales_manager.get_statistics()
        
        st.metric("📝 Total Transacciones", stats['total_transactions'])
        st.metric("🛒 Total Pedidos", f"${stats['total_sales']:,.2f}")
        st.metric("💵 Total Pagos", f"${stats['total_payments']:,.2f}")
        st.metric("⚖️ Balance Neto", f"${stats['net_balance']:,.2f}")
        st.metric("👥 Clientes Únicos", stats['unique_clients'])
        st.metric("📦 Productos Únicos", stats['unique_products'])
    
    # Tabs para separar funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏪 Operaciones", "📊 Visualización por Cliente", "✏️ Edición de Cliente", "💰 Lista de Precios", "⚙️ Administración"])
    
    # TAB 1: OPERACIONES (Pedido, Pago, Pago Inmediato)
    with tab1:
        st.subheader("🏪 Gestión de Pedidos y Pagos")
        
        # Selector del tipo de operación
        tipo_operacion = st.radio(
            "🔄 Selecciona el tipo de operación:",
            options=["Pedido", "Pago", "Pago Inmediato"],
            horizontal=True,
            help="Pedido: Solo registra pedido | Pago: Solo registra pago | Pago Inmediato: Registra pedido + pago automáticamente"
        )
        
        st.markdown("---")
        
        # Información común
        col1, col2 = st.columns(2)
        
        with col1:
            # Selección de cliente
            clientes = st.session_state.sales_manager.get_client_names()
            cliente_seleccionado = st.selectbox(
                "👤 Cliente",
                options=[""] + clientes,
                key="cliente_select"
            )
        
        with col2:
            # Comentarios
            comentarios = st.text_area(
                "💬 Comentarios",
                key="comentarios_input",
                height=80
            )
        
        # Campos específicos según el tipo de operación
        if tipo_operacion == "Pedido":
            st.subheader("🛒 Crear Pedido con Carrito")
            
            # Buscador y botón de agregar
            col_search, col_add = st.columns([3, 1])
            
            with col_search:
                search_term = st.text_input(
                    "🔍 Buscar producto por código o nombre",
                    placeholder="Ej: brake, 1234, pedal...",
                    key="product_search_carrito"
                )
                
                if search_term and st.button("🔍 Buscar", key="search_btn_carrito"):
                    search_products(search_term)
            
            with col_add:
                st.write("")
                st.write("")
                if st.button("🗑️ Limpiar Búsqueda", key="clear_search_carrito"):
                    st.session_state.search_results = []
                    st.rerun()
            
            # Mostrar resultados de búsqueda con botón de agregar
            if st.session_state.search_results:
                st.write("**📋 Resultados de Búsqueda:**")
                
                for i, (code, spanish, english) in enumerate(st.session_state.search_results):
                    display_name = spanish if spanish else english
                    
                    col_product, col_price, col_qty, col_add_btn = st.columns([3, 1, 1, 1])
                    
                    with col_product:
                        st.write(f"**{code}** - {display_name[:40]}{'...' if len(display_name) > 40 else ''}")
                    
                    with col_price:
                        precio = st.session_state.sales_manager.get_product_sell_price(code)
                        st.write(f"${precio:,.2f}")
                    
                    with col_qty:
                        cantidad = st.number_input(
                            "Cant.", 
                            min_value=1, 
                            value=1, 
                            key=f"qty_{code}_{i}",
                            step=1
                        )
                    
                    with col_add_btn:
                        if st.button("➕", key=f"add_{code}_{i}"):
                            add_to_cart(code, display_name, precio, cantidad)
                            st.success(f"✅ {display_name} agregado al carrito")
                            st.rerun()
            
            # Sección para elementos personalizados (sin código de producto)
            st.markdown("---")
            st.subheader("📝 Agregar Elemento Personalizado")
            st.info("💡 Para elementos como 'Deudas Previas', 'Servicios', 'Descuentos', etc.")
            
            col_custom_desc, col_custom_price, col_custom_qty, col_custom_add = st.columns([3, 1, 1, 1])
            
            with col_custom_desc:
                descripcion_custom = st.text_input(
                    "Descripción del elemento",
                    placeholder="Ej: Deuda previa, Servicio técnico, Descuento...",
                    key="descripcion_custom"
                )
            
            with col_custom_price:
                precio_custom = st.number_input(
                    "Precio USD",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    key="precio_custom"
                )
            
            with col_custom_qty:
                cantidad_custom = st.number_input(
                    "Cantidad",
                    min_value=1,
                    value=1,
                    step=1,
                    key="cantidad_custom"
                )
            
            with col_custom_add:
                st.write("")  # Espaciado para alinear
                if st.button("➕ Agregar", key="add_custom"):
                    if descripcion_custom.strip() and precio_custom > 0:
                        # Generar código personalizado para elementos sin código
                        codigo_custom = f"CUSTOM-{len(st.session_state.carrito_pedido) + 1:03d}"
                        add_to_cart(codigo_custom, descripcion_custom.strip(), precio_custom, cantidad_custom)
                        st.success(f"✅ {descripcion_custom.strip()} agregado al carrito")
                        # Limpiar campos después de agregar
                        st.session_state.descripcion_custom = ""
                        st.session_state.precio_custom = 0.0
                        st.session_state.cantidad_custom = 1
                        st.rerun()
                    else:
                        st.error("❌ Complete la descripción y el precio")
            
            # Mostrar carrito
            st.markdown("---")
            st.subheader("🛒 Carrito de Pedido")
            
            if st.session_state.carrito_pedido:
                # Mostrar productos en el carrito
                for i, item in enumerate(st.session_state.carrito_pedido):
                    col_prod, col_precio, col_cant, col_subtotal, col_remove = st.columns([3, 1, 1, 1, 1])
                    
                    with col_prod:
                        st.write(f"**{item['codigo']}** - {item['nombre'][:30]}{'...' if len(item['nombre']) > 30 else ''}")
                    
                    with col_precio:
                        st.write(f"${item['precio_unitario']:,.2f}")
                    
                    with col_cant:
                        new_qty = st.number_input(
                            "Cant.", 
                            min_value=1, 
                            value=item['cantidad'],
                            key=f"cart_qty_{i}",
                            step=1
                        )
                        if new_qty != item['cantidad']:
                            st.session_state.carrito_pedido[i]['cantidad'] = new_qty
                            st.session_state.carrito_pedido[i]['subtotal'] = item['precio_unitario'] * new_qty
                            update_total()
                            st.rerun()
                    
                    with col_subtotal:
                        st.write(f"${item['subtotal']:,.2f}")
                    
                    with col_remove:
                        if st.button("🗑️", key=f"remove_{i}"):
                            remove_from_cart(i)
                            st.rerun()
                
                # Total y controles del carrito
                col_total, col_clear = st.columns(2)
                
                with col_total:
                    st.metric("💰 Total del Pedido", f"${st.session_state.total_pedido:,.2f}")
                
                with col_clear:
                    if st.button("🗑️ Limpiar Carrito", type="secondary"):
                        clear_cart()
                        st.rerun()
            
            else:
                st.info("🛒 El carrito está vacío. Busca y agrega productos.")
        
        elif tipo_operacion == "Pago Inmediato":
            st.subheader("⚡ Pago Inmediato (Producto único)")
            
            col3, col4 = st.columns([2, 1])
            
            with col3:
                # Búsqueda de producto
                search_term = st.text_input(
                    "🔍 Buscar producto",
                    placeholder="Ej: brake, 1234, pedal...",
                    key="product_search_inmediato"
                )
                
                if search_term and st.button("🔍 Buscar", key="search_btn_inmediato"):
                    search_products(search_term)
                
                # Mostrar resultados y permitir selección
                if st.session_state.search_results:
                    st.write("**Selecciona un producto:**")
                    
                    for i, (code, spanish, english) in enumerate(st.session_state.search_results):
                        display_name = spanish if spanish else english
                        precio = st.session_state.sales_manager.get_product_sell_price(code)
                        
                        if st.button(f"📦 {code} - {display_name[:50]} - ${precio:,.2f}", key=f"select_inmediato_{i}"):
                            st.session_state.selected_product = {
                                'code': code,
                                'name': display_name,
                                'price': precio
                            }
                            st.rerun()
                
                # Mostrar producto seleccionado
                if st.session_state.selected_product:
                    st.success(f"✅ Producto seleccionado: {st.session_state.selected_product['code']} - {st.session_state.selected_product['name']}")
                    
                    if st.button("❌ Cambiar producto"):
                        st.session_state.selected_product = None
                        st.rerun()
            
            with col4:
                # Precio del producto seleccionado
                codigo_pieza = st.session_state.selected_product['code'] if st.session_state.selected_product else ""
                precio_default = st.session_state.selected_product['price'] if st.session_state.selected_product else 0.0
                
                precio_venta = st.number_input(
                    "💰 Precio de Venta",
                    min_value=0.0,
                    value=float(precio_default),
                    step=0.01,
                    format="%.2f",
                    key="precio_input"
                )
        
        elif tipo_operacion == "Pago":
            st.subheader("💵 Información del Pago")
            
            # Selector de tipo de pago
            col7, col8 = st.columns(2)
            
            with col7:
                tipo_pago = st.radio(
                    "💳 Tipo de Pago:",
                    options=["Pago a Pedido Específico", "Pago Varios"],
                    help="Pago a Pedido Específico: Se asocia a un pedido existente | Pago Varios: Pago general no asociado a pedido"
                )
                
                # Campos según tipo de pago
                if tipo_pago == "Pago a Pedido Específico":
                    # Buscar pedidos existentes
                    df_pedidos = st.session_state.sales_manager.load_pedidos()
                    if not df_pedidos.empty and cliente_seleccionado:
                        pedidos_cliente = df_pedidos[df_pedidos['Cliente'] == cliente_seleccionado]
                        if not pedidos_cliente.empty:
                            opciones_pedidos = [""] + [f"{row['Numero_Pedido']} - {row['Codigo_Pieza']} - Cant:{row['Cantidad']} (${row['Precio_Total']})" 
                                                     for _, row in pedidos_cliente.iterrows()]
                            pedido_seleccionado = st.selectbox(
                                "📋 Seleccionar Pedido a Pagar",
                                options=opciones_pedidos,
                                key="pedido_ref_select"
                            )
                            
                            if pedido_seleccionado:
                                numero_pedido_ref = pedido_seleccionado.split(" - ")[0]
                                codigo_pieza_ref = pedido_seleccionado.split(" - ")[1]
                                # Extraer precio total del pedido seleccionado para auto-completar
                                precio_total_str = pedido_seleccionado.split("($")[1].split(")")[0]
                                precio_total_default = float(precio_total_str)
                            else:
                                numero_pedido_ref = ""
                                codigo_pieza_ref = ""
                                precio_total_default = 0.0
                        else:
                            numero_pedido_ref = ""
                            codigo_pieza_ref = ""
                            precio_total_default = 0.0
                            st.info("No hay pedidos pendientes para este cliente")
                    else:
                        numero_pedido_ref = st.text_input(
                            "📋 Número de Pedido",
                            placeholder="Ej: PED001",
                            key="pedido_ref_manual"
                        )
                        codigo_pieza_ref = st.text_input(
                            "🏷️ Código de Pieza",
                            placeholder="Ej: ABC123",
                            key="codigo_ref_manual"
                        )
                        precio_total_default = 0.0  # No hay auto-completado para entrada manual
                
                else:  # Pago Varios
                    st.info("💡 **Pago Varios:** Este pago no se asociará a un pedido específico")
                    numero_pedido_ref = ""
                    codigo_pieza_ref = ""
                    precio_total_default = 0.0  # No hay auto-completado para pagos varios
                    
                    # Campo adicional para descripción del pago varios
                    descripcion_pago = st.text_input(
                        "📝 Descripción del Pago",
                        placeholder="Ej: Anticipo, Pago a cuenta, Servicios, etc.",
                        key="descripcion_pago_varios"
                    )
            
            with col8:
                # Determinar valor por defecto según el tipo de pago y pedido seleccionado
                if tipo_pago == "Pago a Pedido Específico" and pedido_seleccionado and precio_total_default > 0:
                    monto_default = precio_total_default
                else:
                    monto_default = 0.01
                
                monto_pago = st.number_input(
                    "💰 Monto del Pago",
                    min_value=0.01,
                    value=monto_default,
                    step=0.01,
                    format="%.2f",
                    key="monto_pago_input"
                )
                
                if tipo_pago == "Pago Varios":
                    st.write("**📋 Resumen:**")
                    st.write(f"- Tipo: Pago Varios")
                    st.write(f"- Cliente: {cliente_seleccionado if cliente_seleccionado else 'No seleccionado'}")
                    st.write(f"- Monto: ${monto_pago:,.2f}")
                    descripcion = st.session_state.get('descripcion_pago_varios', '')
                    if descripcion:
                        st.write(f"- Descripción: {descripcion}")
        
        # Botón de registro (solo para operaciones que no sean visualización)
        st.markdown("---")
        col_btn = st.columns([2, 1, 2])
        
        with col_btn[1]:
            if st.button(f"✅ Registrar {tipo_operacion}", key="register_btn", type="primary", use_container_width=True):
                # Validaciones comunes
                if not cliente_seleccionado:
                    st.error("❌ Debe seleccionar un cliente")
                else:
                    if tipo_operacion == "Pedido":
                        if not st.session_state.carrito_pedido:
                            st.error("❌ Debe agregar al menos un producto al carrito")
                        else:
                            success, pedido_num = st.session_state.sales_manager.add_pedido_multiple(
                                cliente=cliente_seleccionado,
                                productos_list=st.session_state.carrito_pedido,
                                comentarios=comentarios
                            )
                            
                            if success:
                                st.success(f"✅ Pedido registrado exitosamente - N°: {pedido_num}")
                                clear_cart()
                                st.rerun()
                            else:
                                st.error("❌ Error al registrar el pedido")
                    
                    elif tipo_operacion == "Pago":
                        if tipo_pago == "Pago Varios":
                            success, pago_num = st.session_state.sales_manager.add_pago(
                                cliente=cliente_seleccionado,
                                monto_pago=monto_pago,
                                comentarios=f"PAGO VARIOS - {descripcion_pago}"
                            )
                        else:
                            success, pago_num = st.session_state.sales_manager.add_pago(
                                cliente=cliente_seleccionado,
                                monto_pago=monto_pago,
                                numero_pedido_ref=numero_pedido_ref,
                                codigo_pieza_ref=codigo_pieza_ref,
                                comentarios=comentarios
                            )
                        
                        if success:
                            if tipo_pago == "Pago Varios":
                                st.success(f"✅ Pago Varios registrado exitosamente - N°: {pago_num}")
                            else:
                                st.success(f"✅ Pago registrado exitosamente - N°: {pago_num}")
                            st.rerun()
                        else:
                            st.error("❌ Error al registrar el pago")
                    
                    elif tipo_operacion == "Pago Inmediato":
                        if not codigo_pieza:
                            st.error("❌ Debe seleccionar un producto")
                        else:
                            success, pedido_num, pago_num = st.session_state.sales_manager.add_pago_inmediato(
                                cliente=cliente_seleccionado,
                                codigo_pieza=codigo_pieza,
                                precio_venta=precio_venta,
                                comentarios=comentarios
                            )
                            
                            if success:
                                st.success(f"✅ Pago inmediato registrado - Pedido: {pedido_num}, Pago: {pago_num}")
                                # Limpiar formulario
                                st.session_state.selected_product = None
                                st.session_state.search_results = []
                                st.rerun()
                            else:
                                st.error("❌ Error al registrar el pago inmediato")
    
    # TAB 2: VISUALIZACIÓN POR CLIENTE
    with tab2:
        st.subheader("📊 Visualización por Cliente")
        
        # Selector de cliente para visualización
        clientes = st.session_state.sales_manager.get_client_names()
        cliente_visualizacion = st.selectbox(
            "👤 Seleccionar Cliente para Visualizar",
            options=[""] + clientes,
            key="cliente_visualizacion"
        )
        
        if cliente_visualizacion:
            # Obtener balance del cliente
            balance = st.session_state.sales_manager.get_client_balance(cliente_visualizacion)
            
            # Mostrar balance en el cabezal
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Total Deuda (Pedidos)", 
                    f"${balance['total_deuda']:,.2f}",
                    help="Suma total de todos los pedidos"
                )
            
            with col2:
                st.metric(
                    "💵 Total Pagos", 
                    f"${balance['total_pagos']:,.2f}",
                    help="Suma total de todos los pagos recibidos"
                )
            
            with col3:
                balance_delta = balance['balance']
                st.metric(
                    "⚖️ Balance", 
                    f"${abs(balance_delta):,.2f}",
                    delta=f"{'Debe' if balance_delta > 0 else 'A favor' if balance_delta < 0 else 'Al día'}"
                )
            
            with col4:
                # Indicador visual del estado
                if balance_delta > 0:
                    st.error(f"🔴 Cliente debe ${balance_delta:,.2f}")
                elif balance_delta < 0:
                    st.success(f"🟢 Cliente tiene crédito de ${abs(balance_delta):,.2f}")
                else:
                    st.info("🔵 Cliente al día")
            
            # Tablas en paralelo
            st.markdown("---")
            col_pedidos, col_pagos = st.columns(2)
            
            with col_pedidos:
                st.subheader("📋 Historial de Pedidos")
                
                df_pedidos = st.session_state.sales_manager.get_client_pedidos(cliente_visualizacion)
                
                if not df_pedidos.empty:
                    # Formatear las fechas y mostrar solo las columnas relevantes
                    df_display_pedidos = df_pedidos.copy()
                    df_display_pedidos['Fecha'] = pd.to_datetime(df_display_pedidos['Fecha']).dt.strftime('%d/%m/%Y %H:%M')
                    
                    # Seleccionar y renombrar columnas para mejor visualización (sin Estado)
                    cols_to_show = ['Fecha', 'Numero_Pedido', 'Codigo_Pieza', 'Nombre_Pieza', 'Cantidad', 'Precio_Total']
                    df_display_pedidos = df_display_pedidos[cols_to_show]
                    df_display_pedidos.columns = ['Fecha', 'Nº Pedido', 'Código', 'Producto', 'Cant.', 'Total']
                    
                    st.dataframe(
                        df_display_pedidos,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
                    # Total de la tabla de pedidos
                    total_monto_pedidos = df_pedidos['Precio_Total'].sum()
                    st.markdown(f"**💰 Total General de Pedidos: ${total_monto_pedidos:,.2f}**")
                    
                    # Resumen de pedidos
                    total_pedidos = len(df_pedidos)
                    pedidos_pendientes = len(df_pedidos[df_pedidos['Estado_Pedido'] == 'PENDIENTE'])
                    pedidos_pagados = len(df_pedidos[df_pedidos['Estado_Pedido'] == 'PAGADO'])
                    
                    st.write(f"**📊 Resumen:** {total_pedidos} pedidos total | {pedidos_pendientes} pendientes | {pedidos_pagados} pagados")
                    
                else:
                    st.info("📄 No hay pedidos registrados para este cliente")
            
            with col_pagos:
                st.subheader("💵 Historial de Pagos")
                
                df_pagos = st.session_state.sales_manager.get_client_pagos(cliente_visualizacion)
                
                if not df_pagos.empty:
                    # Formatear las fechas y mostrar solo las columnas relevantes
                    df_display_pagos = df_pagos.copy()
                    df_display_pagos['Fecha'] = pd.to_datetime(df_display_pagos['Fecha']).dt.strftime('%d/%m/%Y %H:%M')
                    
                    # Seleccionar y renombrar columnas para mejor visualización
                    cols_to_show = ['Fecha', 'Numero_Pago', 'Numero_Pedido_Ref', 'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios']
                    df_display_pagos = df_display_pagos[cols_to_show]
                    df_display_pagos.columns = ['Fecha', 'Nº Pago', 'Pedido Ref.', 'Código Ref.', 'Monto', 'Comentarios']
                    
                    st.dataframe(
                        df_display_pagos,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
                    # Total de la tabla de pagos
                    total_monto_pagos = df_pagos['Monto_Pago'].sum()
                    st.markdown(f"**💰 Total General de Pagos: ${total_monto_pagos:,.2f}**")
                    
                    # Resumen de pagos
                    total_pagos_count = len(df_pagos)
                    promedio_pago = df_pagos['Monto_Pago'].mean()
                    
                    st.write(f"**📊 Resumen:** {total_pagos_count} pagos total | Promedio: ${promedio_pago:,.2f}")
                    
                else:
                    st.info("📄 No hay pagos registrados para este cliente")
        else:
            st.info("👆 Selecciona un cliente para ver su historial de pedidos y pagos")
    
    # Pestaña 3: Edición de Cliente
    with tab3:
        st.subheader("✏️ Edición de Cliente")
        
        # Selector de cliente para edición
        clientes = st.session_state.sales_manager.get_client_names()
        cliente_edicion = st.selectbox(
            "👤 Seleccionar Cliente para Editar",
            options=[""] + clientes,
            key="cliente_edicion"
        )
        
        if cliente_edicion:
            st.markdown("---")
            st.info("⚠️ **Nota:** Ocultar un registro lo mantiene en la base de datos pero no aparece en visualizaciones. Eliminar lo borra permanentemente.")
            
            # Obtener todos los registros (incluyendo ocultos)
            df_pedidos_todos = st.session_state.sales_manager.get_client_pedidos(cliente_edicion, incluir_ocultos=True)
            df_pagos_todos = st.session_state.sales_manager.get_client_pagos(cliente_edicion, incluir_ocultos=True)
            
            # Tablas en paralelo
            col_edit_pedidos, col_edit_pagos = st.columns(2)
            
            with col_edit_pedidos:
                st.subheader("📋 Editar Pedidos")
                
                if not df_pedidos_todos.empty:
                    # Procesar cada pedido con opciones de edición
                    for idx, row in df_pedidos_todos.iterrows():
                        estado_vis = row.get('EstadoVisualizacion', 'Visible')
                        
                        # Contenedor expandible para cada pedido
                        with st.expander(f"🔹 {row['Numero_Pedido']} - ${row['Precio_Total']:,.2f} {'(OCULTO)' if estado_vis == 'Oculto' else ''}"):
                            
                            # Información del pedido
                            st.write(f"**Fecha:** {row['Fecha']}")
                            st.write(f"**Producto:** {row['Nombre_Pieza']}")
                            st.write(f"**Código:** {row['Codigo_Pieza']}")
                            st.write(f"**Cantidad:** {row['Cantidad']}")
                            st.write(f"**Total:** ${row['Precio_Total']:,.2f}")
                            st.write(f"**Estado:** {estado_vis}")
                            
                            # Botones de acción
                            col_btn1, col_btn2 = st.columns(2)
                            
                            with col_btn1:
                                if estado_vis == 'Visible':
                                    if st.button(f"👁️‍🗨️ Ocultar", key=f"ocultar_pedido_{row['Numero_Pedido']}"):
                                        if st.session_state.sales_manager.ocultar_pedido(row['Numero_Pedido']):
                                            st.success("✅ Pedido ocultado")
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al ocultar pedido")
                                else:
                                    if st.button(f"👁️ Mostrar", key=f"mostrar_pedido_{row['Numero_Pedido']}"):
                                        if st.session_state.sales_manager.mostrar_pedido(row['Numero_Pedido']):
                                            st.success("✅ Pedido visible nuevamente")
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al mostrar pedido")
                            
                            with col_btn2:
                                if st.button(f"🗑️ Eliminar", key=f"eliminar_pedido_{row['Numero_Pedido']}", type="secondary"):
                                    if st.session_state.sales_manager.eliminar_pedido(row['Numero_Pedido']):
                                        st.success("✅ Pedido eliminado permanentemente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al eliminar pedido")
                else:
                    st.info("📄 No hay pedidos para este cliente")
            
            with col_edit_pagos:
                st.subheader("💵 Editar Pagos")
                
                if not df_pagos_todos.empty:
                    # Procesar cada pago con opciones de edición
                    for idx, row in df_pagos_todos.iterrows():
                        estado_vis = row.get('EstadoVisualizacion', 'Visible')
                        
                        # Contenedor expandible para cada pago
                        with st.expander(f"🔹 {row['Numero_Pago']} - ${row['Monto_Pago']:,.2f} {'(OCULTO)' if estado_vis == 'Oculto' else ''}"):
                            
                            # Información del pago
                            st.write(f"**Fecha:** {row['Fecha']}")
                            st.write(f"**Monto:** ${row['Monto_Pago']:,.2f}")
                            if row['Numero_Pedido_Ref']:
                                st.write(f"**Pedido Ref.:** {row['Numero_Pedido_Ref']}")
                            if row['Codigo_Pieza_Ref']:
                                st.write(f"**Código Ref.:** {row['Codigo_Pieza_Ref']}")
                            if row['Comentarios']:
                                st.write(f"**Comentarios:** {row['Comentarios']}")
                            st.write(f"**Estado:** {estado_vis}")
                            
                            # Botones de acción
                            col_btn1, col_btn2 = st.columns(2)
                            
                            with col_btn1:
                                if estado_vis == 'Visible':
                                    if st.button(f"👁️‍🗨️ Ocultar", key=f"ocultar_pago_{row['Numero_Pago']}"):
                                        if st.session_state.sales_manager.ocultar_pago(row['Numero_Pago']):
                                            st.success("✅ Pago ocultado")
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al ocultar pago")
                                else:
                                    if st.button(f"👁️ Mostrar", key=f"mostrar_pago_{row['Numero_Pago']}"):
                                        if st.session_state.sales_manager.mostrar_pago(row['Numero_Pago']):
                                            st.success("✅ Pago visible nuevamente")
                                            st.rerun()
                                        else:
                                            st.error("❌ Error al mostrar pago")
                            
                            with col_btn2:
                                if st.button(f"🗑️ Eliminar", key=f"eliminar_pago_{row['Numero_Pago']}", type="secondary"):
                                    if st.session_state.sales_manager.eliminar_pago(row['Numero_Pago']):
                                        st.success("✅ Pago eliminado permanentemente")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al eliminar pago")
                else:
                    st.info("📄 No hay pagos para este cliente")
        else:
            st.info("👆 Selecciona un cliente para editar sus registros")
    
    # Pestaña 4: Lista de Precios
    with tab4:
        st.subheader("💰 Lista de Precios")
        
        # Búsqueda en la lista de precios
        col_buscar, col_stats = st.columns([2, 1])
        
        with col_buscar:
            buscar_precio = st.text_input(
                "🔍 Buscar por código o nombre en español",
                placeholder="Ingrese código de producto o nombre...",
                key="buscar_lista_precios"
            )
        
        with col_stats:
            # Estadísticas rápidas de productos
            total_productos = len(st.session_state.sales_manager.products_data)
            productos_con_espanol = sum(1 for p in st.session_state.sales_manager.products_data.values() if p.get('espanol'))
            
            st.metric("📦 Total Productos", total_productos)
            st.metric("🇪🇸 Con Español", productos_con_espanol)
        
        st.markdown("---")
        
        # Mostrar resultados de búsqueda o lista completa
        if buscar_precio:
            # Buscar productos manualmente en products_data
            productos_filtrados = {}
            buscar_lower = buscar_precio.lower()
            
            for codigo, producto in st.session_state.sales_manager.products_data.items():
                nombre_esp = producto.get('espanol', '').lower() if producto.get('espanol') else ''
                codigo_lower = codigo.lower()
                
                if buscar_lower in codigo_lower or buscar_lower in nombre_esp:
                    productos_filtrados[codigo] = producto
            
            if productos_filtrados:
                st.write(f"**📋 {len(productos_filtrados)} resultado(s) encontrado(s):**")
                
                # Crear DataFrame para mostrar resultados
                data_resultados = []
                for codigo, producto in productos_filtrados.items():
                    nombre_esp = producto.get('espanol', '')
                    nombre_ing = producto.get('name', '')
                    nombre_display = nombre_esp if nombre_esp else nombre_ing
                    precio = st.session_state.sales_manager.get_product_sell_price(codigo)
                    
                    data_resultados.append({
                        'Código': codigo,
                        'Nombre': nombre_display,
                        'Precio (USD)': f"${precio:,.2f}"
                    })
                
                df_resultados = pd.DataFrame(data_resultados)
                
                # Mostrar tabla
                st.dataframe(df_resultados, use_container_width=True, hide_index=True)
                
                # Opción de descarga
                if len(df_resultados) > 0:
                    csv_data = df_resultados.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar resultados como CSV",
                        data=csv_data,
                        file_name=f"busqueda_precios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No se encontraron productos con ese criterio de búsqueda")
        else:
            st.info("💡 Ingrese un término de búsqueda para ver productos específicos")
            
            # Mostrar algunos productos de ejemplo
            st.subheader("🎯 Productos de Ejemplo")
            
            # Tomar una muestra de productos para mostrar
            sample_products = list(st.session_state.sales_manager.products_data.items())[:10]
            
            if sample_products:
                data_ejemplo = []
                for codigo, producto in sample_products:
                    precio = st.session_state.sales_manager.get_product_sell_price(codigo)
                    nombre_esp = producto.get('espanol', '')
                    nombre_ing = producto.get('name', '')
                    nombre_display = nombre_esp if nombre_esp else nombre_ing
                    
                    data_ejemplo.append({
                        'Código': codigo,
                        'Nombre': nombre_display,
                        'Precio (USD)': f"${precio:,.2f}"
                    })
                
                df_ejemplo = pd.DataFrame(data_ejemplo)
                st.dataframe(df_ejemplo, use_container_width=True, hide_index=True)
                
                st.info("💡 Esto es solo una muestra. Use el buscador para encontrar productos específicos.")
    
    # Pestaña 5: Administración
    with tab5:
        st.subheader("⚙️ Administración de Sistema")
        
        # Estadísticas generales
        stats_admin = st.session_state.sales_manager.obtener_estadisticas_administracion()
        
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.metric("👥 Total Clientes", stats_admin['total_clientes'])
        
        with col_stats2:
            st.metric("📦 Total Productos", stats_admin['total_productos'])
        
        with col_stats3:
            st.metric("🇪🇸 Con Traducción", stats_admin['productos_con_espanol'])
        
        with col_stats4:
            st.metric("🇺🇸 Solo Inglés", stats_admin['productos_sin_espanol'])
        
        st.markdown("---")
        
        # Formularios en dos columnas
        col_clientes, col_productos = st.columns(2)
        
        with col_clientes:
            st.subheader("👥 Agregar Nuevo Cliente")
            
            with st.form("form_nuevo_cliente"):
                nombre_cliente = st.text_input(
                    "📝 Nombre del Cliente",
                    placeholder="Ej: Juan Pérez",
                    help="Ingrese el nombre completo del cliente"
                )
                
                password_cliente = st.text_input(
                    "🔐 Contraseña",
                    value="0000",
                    help="Contraseña por defecto es '0000'"
                )
                
                submit_cliente = st.form_submit_button("✅ Agregar Cliente", type="primary", use_container_width=True)
                
                if submit_cliente:
                    if nombre_cliente.strip():
                        success, message = st.session_state.sales_manager.agregar_cliente(
                            nombre_cliente.strip(),
                            password_cliente.strip()
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            # Recargar datos de clientes
                            st.session_state.sales_manager._load_clients()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ El nombre del cliente es obligatorio")
            
            # Lista de clientes existentes
            st.subheader("📋 Clientes Existentes")
            clientes_existentes = st.session_state.sales_manager.get_client_names()
            
            if clientes_existentes:
                with st.expander(f"Ver {len(clientes_existentes)} clientes"):
                    for i, cliente in enumerate(clientes_existentes, 1):
                        st.write(f"{i}. {cliente}")
            else:
                st.info("No hay clientes registrados")
        
        with col_productos:
            col_titulo, col_reload = st.columns([3, 1])
            
            with col_titulo:
                st.subheader("📦 Agregar Nuevo Producto")
            
            with col_reload:
                if st.button("🔄 Recargar Sistema", help="Reinicia SalesManager para cargar nuevos métodos"):
                    # Forzar recarga importando nuevamente
                    import importlib
                    import sys
                    if 'Functions.SalesManager.SalesManager' in sys.modules:
                        importlib.reload(sys.modules['Functions.SalesManager.SalesManager'])
                    
                    from Functions.SalesManager.SalesManager import SalesManager
                    st.session_state.sales_manager = SalesManager()
                    st.success("✅ Sistema recargado correctamente")
                    st.rerun()
            
            with st.form("form_nuevo_producto"):
                codigo_producto = st.text_input(
                    "🔢 Código del Producto",
                    placeholder="Ej: 2024-001",
                    help="Código único del producto"
                )
                
                nombre_espanol = st.text_input(
                    "🇪🇸 Nombre en Español",
                    placeholder="Ej: Pastillas de freno",
                    help="Nombre del producto en español"
                )
                
                col_costo, col_peso = st.columns(2)
                
                with col_costo:
                    final_cost_usa = st.number_input(
                        "💵 Costo Final USA ($)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help="Costo final en dólares estadounidenses"
                    )
                
                with col_peso:
                    peso_gramos = st.number_input(
                        "⚖️ Peso (gramos)",
                        min_value=0,
                        step=1,
                        help="Peso del producto en gramos (opcional para calcular envío)"
                    )
                
                col_precio, col_auto = st.columns(2)
                
                with col_precio:
                    precio_venta_manual = st.number_input(
                        "💰 Precio de Venta (opcional)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help="Si no se completa, se calculará automáticamente"
                    )
                
                with col_auto:
                    calcular_automatico = st.checkbox(
                        "🤖 Calcular precio automáticamente",
                        value=True,
                        help="Usar las fórmulas de la base de datos para calcular el precio"
                    )
                    
                    # Mostrar vista previa del cálculo si hay datos suficientes
                    if calcular_automatico and final_cost_usa > 0:
                        try:
                            # Importar para cálculo de vista previa
                            import sys
                            import os
                            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Functions', 'DataBaseBuild'))
                            from DataBase import MecatechDatabase
                            
                            db = MecatechDatabase()
                            shipping_cost = db.calculate_shipping_cost(peso_gramos if peso_gramos > 0 else None)
                            costo_in_arg = db.calculate_costo_in_arg(shipping_cost, final_cost_usa)
                            precio_calculado = db.calculate_sell_price(costo_in_arg)
                            
                            st.info(f"💡 Precio calculado: ${precio_calculado:.2f}")
                        except:
                            pass
                
                col_submit, col_update = st.columns([1, 1])
                
                with col_submit:
                    submit_producto = st.form_submit_button("✅ Agregar Producto", type="primary", use_container_width=True)
                
                with col_update:
                    update_all = st.form_submit_button("🔄 Actualizar Todos los Precios", type="secondary", use_container_width=True)
                
                if submit_producto:
                    if codigo_producto.strip() and nombre_espanol.strip() and final_cost_usa > 0:
                        # Determinar el precio de venta
                        if calcular_automatico or precio_venta_manual <= 0:
                            # Usar el cálculo automático de SalesManager
                            precio_final = None  # SalesManager calculará automáticamente
                        else:
                            precio_final = precio_venta_manual
                        
                        # Forzar recarga del SalesManager para obtener método actualizado
                        from Functions.SalesManager.SalesManager import SalesManager
                        sales_manager_temp = SalesManager()
                        
                        success, message = sales_manager_temp.agregar_producto(
                            codigo=codigo_producto.strip().upper(),
                            nombre_espanol=nombre_espanol.strip(),
                            final_cost_usa=final_cost_usa,
                            peso=peso_gramos if peso_gramos > 0 else None,
                            precio_venta=precio_final if precio_final else 0.0
                        )
                        
                        # Actualizar la instancia en session state
                        if success:
                            st.session_state.sales_manager = sales_manager_temp
                        
                        if success:
                            st.success(f"✅ {message}")
                            # Recargar datos de productos
                            st.session_state.sales_manager._load_products()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ El código, nombre en español y costo final USA son obligatorios")
                
                if update_all:
                    # Ejecutar el script de actualización de la base de datos
                    with st.spinner("🔄 Actualizando todos los precios desde la base de datos..."):
                        try:
                            import subprocess
                            import os
                            
                            # Ejecutar el script DataBase.py
                            script_path = os.path.join(os.path.dirname(__file__), '..', 'Functions', 'DataBaseBuild', 'DataBase.py')
                            result = subprocess.run(['python', script_path], capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                st.success("✅ Todos los precios han sido actualizados desde la base de datos")
                                # Recargar productos
                                st.session_state.sales_manager._load_products()
                                st.rerun()
                            else:
                                st.error(f"❌ Error ejecutando actualización: {result.stderr}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            # Búsqueda de productos existentes
            st.subheader("🔍 Buscar Productos Existentes")
            
            buscar_producto = st.text_input(
                "Buscar producto",
                placeholder="Ingrese código o nombre...",
                key="buscar_producto_admin"
            )
            
            if buscar_producto:
                resultados = st.session_state.sales_manager.search_products_by_name(buscar_producto)
                
                if resultados:
                    st.write(f"**📋 {len(resultados)} resultado(s) encontrado(s):**")
                    
                    for codigo, nombre_esp, nombre_ing in resultados[:10]:  # Mostrar solo 10 resultados
                        precio = st.session_state.sales_manager.get_product_sell_price(codigo)
                        nombre_display = nombre_esp if nombre_esp else nombre_ing
                        
                        st.write(f"• **{codigo}:** {nombre_display} - ${precio:,.2f}")
                else:
                    st.info("No se encontraron productos con ese criterio")

if __name__ == "__main__":
    main()