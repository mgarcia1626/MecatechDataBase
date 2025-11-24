"""
Aplicación Streamlit para Gestión de Ventas y Pagos - MecatechDataBase.

Interfaz web simplificada para registrar pedidos, pagos y pagos inmediatos.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import csv
import json

# Configurar paths para importación
current_dir = Path(__file__).parent.resolve()
parent_dir = current_dir.parent
base_project_dir = Path("c:/Users/Matias Garcia/OneDrive - UTN.BA/Repo Nuevo/Mecatech_DataBase/MecatechDataBase")

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

class SalesManager:
    def __init__(self):
        self.base_dir = base_project_dir
        self.pedidos_path = self.base_dir / "DataBase" / "Generated" / "pedidos.csv"
        self.pagos_path = self.base_dir / "DataBase" / "Generated" / "pagos.csv"
        self.clients_path = self.base_dir / "DataBase" / "Generated" / "clientes.json"
        self.products_path = self.base_dir / "DataBase" / "Generated" / "mecatech_database.json"
        
        self.pedidos_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_pedidos_csv()
        self._init_pagos_csv()
        self._load_clients()
        self._load_products()
        
    def _init_pedidos_csv(self):
        if not self.pedidos_path.exists():
            headers = ['Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 'Precio_Unitario', 'Cantidad', 'Precio_Total', 'Estado_Pedido', 'Comentarios', 'EstadoVisualizacion']
            with open(self.pedidos_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    def _init_pagos_csv(self):
        if not self.pagos_path.exists():
            headers = ['Fecha', 'Numero_Pago', 'Cliente', 'Numero_Pedido_Ref', 'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios', 'EstadoVisualizacion']
            with open(self.pagos_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    def _load_clients(self):
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
    
    def get_client_names(self):
        return [client["nombre"] for client in self.clients_data["clientes"]]
    
    def search_products_by_name(self, search_term):
        results = []
        if not search_term:
            return results
            
        search_term = search_term.lower()
        for code, product in self.products_data.items():
            name_english = product.get('name', '').lower()
            name_spanish = product.get('espanol', '').lower() if product.get('espanol') else ''
            
            if (search_term in name_english or 
                search_term in name_spanish or 
                search_term in code.lower()):
                
                display_spanish = product.get('espanol', '')
                display_english = product.get('name', '')
                results.append((code, display_spanish, display_english))
        
        return results[:20]
    
    def get_product_sell_price(self, code):
        product = self.products_data.get(code)
        if not product:
            return 0.0
        arg_data = product.get('ARG', {})
        return float(arg_data.get('Sell_price', 0.0))
    
    def generate_pedido_number(self):
        """Genera un número de pedido automático."""
        try:
            df = self.load_pedidos()
            if df.empty:
                return "PED001"
            
            # Obtener el último número de pedido
            last_orders = df['Numero_Pedido'].str.extract(r'PED(\d+)').astype(int)
            if not last_orders.empty:
                next_num = last_orders[0].max() + 1
                return f"PED{next_num:03d}"
            else:
                return "PED001"
        except:
            return "PED001"
    
    def generate_pago_number(self):
        """Genera un número de pago automático."""
        try:
            df = self.load_pagos()
            if df.empty:
                return "PAG001"
            
            # Obtener el último número de pago
            last_payments = df['Numero_Pago'].str.extract(r'PAG(\d+)').astype(int)
            if not last_payments.empty:
                next_num = last_payments[0].max() + 1
                return f"PAG{next_num:03d}"
            else:
                return "PAG001"
        except:
            return "PAG001"

    def add_pedido(self, cliente, codigo_pieza, precio_venta=None, comentarios="", numero_pedido=None):
        """Agrega un pedido al CSV de pedidos."""
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if numero_pedido is None:
                numero_pedido = self.generate_pedido_number()
            
            if precio_venta is None:
                precio_venta = self.get_product_sell_price(codigo_pieza)
            
            product_name = self.products_data.get(codigo_pieza, {}).get('espanol') or \
                          self.products_data.get(codigo_pieza, {}).get('name', 'Producto no encontrado')
            
            row = [fecha_actual, numero_pedido, cliente, codigo_pieza, product_name, precio_venta, 1, precio_venta, "PENDIENTE", comentarios]
            
            with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pedido
            
        except Exception as e:
            st.error(f"Error al agregar pedido: {e}")
            return False, None
    
    def add_pedido_multiple(self, cliente, productos_list, comentarios=""):
        """Agrega múltiples productos en un solo pedido."""
        try:
            if not productos_list:
                return False, None
                
            numero_pedido = self.generate_pedido_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for item in productos_list:
                    codigo_pieza = item['codigo']
                    precio_unitario = item['precio_unitario'] 
                    cantidad = item['cantidad']
                    subtotal = item['subtotal']
                    
                    product_name = self.products_data.get(codigo_pieza, {}).get('espanol') or \
                                  self.products_data.get(codigo_pieza, {}).get('name', 'Producto no encontrado')
                    
                    row = [fecha_actual, numero_pedido, cliente, codigo_pieza, product_name, 
                          precio_unitario, cantidad, subtotal, "PENDIENTE", comentarios, "Visible"]
                    writer.writerow(row)
            
            return True, numero_pedido
            
        except Exception as e:
            st.error(f"Error al agregar pedido múltiple: {e}")
            return False, None

    def add_pago(self, cliente, monto_pago, numero_pedido_ref="", codigo_pieza_ref="", comentarios=""):
        """Agrega un pago al CSV de pagos."""
        try:
            numero_pago = self.generate_pago_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row = [fecha_actual, numero_pago, cliente, numero_pedido_ref, codigo_pieza_ref, monto_pago, comentarios, "Visible"]
            
            with open(self.pagos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pago
            
        except Exception as e:
            st.error(f"Error al agregar pago: {e}")
            return False, None

    def add_pago_inmediato(self, cliente, codigo_pieza, precio_venta, comentarios=""):
        """Crea un pedido y un pago inmediato."""
        try:
            # Crear pedido
            success_pedido, numero_pedido = self.add_pedido(cliente, codigo_pieza, precio_venta, comentarios)
            
            if success_pedido:
                # Crear pago inmediato
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
    
    def load_pedidos(self):
        try:
            if self.pedidos_path.exists():
                return pd.read_csv(self.pedidos_path)
            else:
                return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def load_pagos(self):
        try:
            if self.pagos_path.exists():
                return pd.read_csv(self.pagos_path)
            else:
                return pd.DataFrame()
        except:
            return pd.DataFrame()
    
    def get_statistics(self):
        df_pedidos = self.load_pedidos()
        df_pagos = self.load_pagos()
        
        total_pedidos = len(df_pedidos) if not df_pedidos.empty else 0
        total_pagos_count = len(df_pagos) if not df_pagos.empty else 0
        total_transactions = total_pedidos + total_pagos_count
        
        total_sales = df_pedidos['Precio_Total'].sum() if not df_pedidos.empty else 0.0
        total_payments = df_pagos['Monto_Pago'].sum() if not df_pagos.empty else 0.0
        
        unique_clients_pedidos = set(df_pedidos['Cliente'].unique()) if not df_pedidos.empty else set()
        unique_clients_pagos = set(df_pagos['Cliente'].unique()) if not df_pagos.empty else set()
        unique_clients = len(unique_clients_pedidos.union(unique_clients_pagos))
        
        unique_products = len(df_pedidos['Codigo_Pieza'].unique()) if not df_pedidos.empty else 0
        
        return {
            "total_transactions": total_transactions,
            "total_sales": round(total_sales, 2),
            "total_payments": round(total_payments, 2),
            "net_balance": round(total_sales - total_payments, 2),
            "unique_clients": unique_clients,
            "unique_products": unique_products
        }
    
    def get_client_pedidos(self, cliente, incluir_ocultos=False):
        """Obtiene todos los pedidos de un cliente específico."""
        df_pedidos = self.load_pedidos()
        if df_pedidos.empty:
            return pd.DataFrame()
        
        # Filtrar por cliente
        df_filtrado = df_pedidos[df_pedidos['Cliente'] == cliente]
        
        # Filtrar por estado de visualización si no se incluyen ocultos
        if not incluir_ocultos and 'EstadoVisualizacion' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['EstadoVisualizacion'] == 'Visible']
        
        return df_filtrado.sort_values('Fecha', ascending=False)
    
    def get_client_pagos(self, cliente, incluir_ocultos=False):
        """Obtiene todos los pagos de un cliente específico."""
        df_pagos = self.load_pagos()
        if df_pagos.empty:
            return pd.DataFrame()
        
        # Filtrar por cliente
        df_filtrado = df_pagos[df_pagos['Cliente'] == cliente]
        
        # Filtrar por estado de visualización si no se incluyen ocultos
        if not incluir_ocultos and 'EstadoVisualizacion' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['EstadoVisualizacion'] == 'Visible']
        
        return df_filtrado.sort_values('Fecha', ascending=False)
    
    def get_client_balance(self, cliente):
        """Calcula el balance de un cliente específico."""
        df_pedidos = self.get_client_pedidos(cliente)
        df_pagos = self.get_client_pagos(cliente)
        
        # Total de pedidos (deuda)
        total_deuda = df_pedidos['Precio_Total'].sum() if not df_pedidos.empty else 0.0
        
        # Total de pagos
        total_pagos = df_pagos['Monto_Pago'].sum() if not df_pagos.empty else 0.0
        
        # Balance (positivo = debe dinero, negativo = tiene crédito)
        balance = total_deuda - total_pagos
        
        return {
            "total_deuda": round(total_deuda, 2),
            "total_pagos": round(total_pagos, 2),
            "balance": round(balance, 2)
        }
    
    def ocultar_pedido(self, numero_pedido):
        """Oculta un pedido cambiando su EstadoVisualizacion a 'Oculto'."""
        try:
            df = self.load_pedidos()
            if df.empty:
                return False
            
            # Buscar el registro y cambiar el estado
            mask = df['Numero_Pedido'] == numero_pedido
            if not mask.any():
                return False
            
            df.loc[mask, 'EstadoVisualizacion'] = 'Oculto'
            
            # Guardar el archivo actualizado
            df.to_csv(self.pedidos_path, index=False)
            return True
            
        except Exception as e:
            print(f"❌ Error ocultando pedido: {e}")
            return False
    
    def ocultar_pago(self, numero_pago):
        """Oculta un pago cambiando su EstadoVisualizacion a 'Oculto'."""
        try:
            df = self.load_pagos()
            if df.empty:
                return False
            
            # Buscar el registro y cambiar el estado
            mask = df['Numero_Pago'] == numero_pago
            if not mask.any():
                return False
            
            df.loc[mask, 'EstadoVisualizacion'] = 'Oculto'
            
            # Guardar el archivo actualizado
            df.to_csv(self.pagos_path, index=False)
            return True
            
        except Exception as e:
            print(f"❌ Error ocultando pago: {e}")
            return False
    
    def eliminar_pedido(self, numero_pedido):
        """Elimina permanentemente un pedido de la base de datos."""
        try:
            df = self.load_pedidos()
            if df.empty:
                return False
            
            # Filtrar para eliminar el registro
            df_filtrado = df[df['Numero_Pedido'] != numero_pedido]
            
            if len(df_filtrado) == len(df):
                return False  # No se encontró el registro
            
            # Guardar el archivo actualizado
            df_filtrado.to_csv(self.pedidos_path, index=False)
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando pedido: {e}")
            return False
    
    def eliminar_pago(self, numero_pago):
        """Elimina permanentemente un pago de la base de datos."""
        try:
            df = self.load_pagos()
            if df.empty:
                return False
            
            # Filtrar para eliminar el registro
            df_filtrado = df[df['Numero_Pago'] != numero_pago]
            
            if len(df_filtrado) == len(df):
                return False  # No se encontró el registro
            
            # Guardar el archivo actualizado
            df_filtrado.to_csv(self.pagos_path, index=False)
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando pago: {e}")
            return False

    def agregar_cliente(self, nombre, password="0000"):
        """Agrega un nuevo cliente al archivo clientes.json."""
        try:
            # Verificar si el cliente ya existe
            nombres_existentes = [c["nombre"].lower() for c in self.clients_data["clientes"]]
            if nombre.lower() in nombres_existentes:
                return False, "El cliente ya existe"
            
            # Agregar nuevo cliente
            nuevo_cliente = {
                "nombre": nombre,
                "password": password
            }
            
            self.clients_data["clientes"].append(nuevo_cliente)
            
            # Guardar el archivo actualizado
            with open(self.clients_path, 'w', encoding='utf-8') as f:
                json.dump(self.clients_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Cliente '{nombre}' agregado exitosamente"
            
        except Exception as e:
            return False, str(e)

    def agregar_producto(self, codigo, nombre_ingles, nombre_espanol="", precio_venta=0.0, peso=None):
        """Agrega un nuevo producto al archivo mecatech_database.json."""
        try:
            # Verificar si el producto ya existe
            if codigo in self.products_data:
                return False, f"El producto con código '{codigo}' ya existe"
            
            # Crear estructura del producto
            nuevo_producto = {
                "name": nombre_ingles,
                "espanol": nombre_espanol if nombre_espanol else None,
                "qty_for_bag": 1,
                "dealer_price": 0.0,
                "consumer_price": 0.0,
                "total_in_usa": 0.0,
                "cost_in_usa_usd": 0.0,
                "final_cost_usa": 0.0,
                "ARG": {
                    "weight": peso,
                    "shipping_cost": 5.0,
                    "Costo_In_Arg": 0.0,
                    "Ref_Price": 0.0,
                    "Sell_price": precio_venta,
                    "Reference_percent": 0.0
                }
            }
            
            # Agregar el producto al diccionario
            self.products_data[codigo] = nuevo_producto
            
            # Guardar el archivo actualizado
            with open(self.products_path, 'w', encoding='utf-8') as f:
                json.dump(self.products_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Producto '{codigo}' agregado exitosamente"
            
        except Exception as e:
            return False, str(e)

    def obtener_estadisticas_administracion(self):
        """Obtiene estadísticas para la sección de administración."""
        try:
            total_clientes = len(self.get_client_names())
            total_productos = len(self.products_data)
            
            # Productos con y sin nombre en español
            productos_con_espanol = sum(1 for p in self.products_data.values() if p.get('espanol'))
            productos_sin_espanol = total_productos - productos_con_espanol
            
            return {
                "total_clientes": total_clientes,
                "total_productos": total_productos,
                "productos_con_espanol": productos_con_espanol,
                "productos_sin_espanol": productos_sin_espanol
            }
            
        except Exception as e:
            return {
                "total_clientes": 0,
                "total_productos": 0,
                "productos_con_espanol": 0,
                "productos_sin_espanol": 0
            }

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
        st.subheader("📊 Estadísticas Generales")
        stats = st.session_state.sales_manager.get_statistics()
        
        st.metric("📝 Total Transacciones", stats['total_transactions'])
        st.metric("🛒 Total Pedidos", f"${stats['total_sales']:,.2f}")
        st.metric("💵 Total Pagos", f"${stats['total_payments']:,.2f}")
        st.metric("⚖️ Balance Neto", f"${stats['net_balance']:,.2f}")
        st.metric("👥 Clientes Únicos", stats['unique_clients'])
        st.metric("📦 Productos Únicos", stats['unique_products'])
    
    # Tabs para separar funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs(["🏪 Operaciones", "📊 Visualización por Cliente", "✏️ Edición de Cliente", "⚙️ Administración"])
    
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
                                        # Función para mostrar (cambiar a Visible)
                                        try:
                                            df_temp = st.session_state.sales_manager.load_pedidos()
                                            mask = df_temp['Numero_Pedido'] == row['Numero_Pedido']
                                            df_temp.loc[mask, 'EstadoVisualizacion'] = 'Visible'
                                            df_temp.to_csv(st.session_state.sales_manager.pedidos_path, index=False)
                                            st.success("✅ Pedido visible nuevamente")
                                            st.rerun()
                                        except:
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
                                        # Función para mostrar (cambiar a Visible)
                                        try:
                                            df_temp = st.session_state.sales_manager.load_pagos()
                                            mask = df_temp['Numero_Pago'] == row['Numero_Pago']
                                            df_temp.loc[mask, 'EstadoVisualizacion'] = 'Visible'
                                            df_temp.to_csv(st.session_state.sales_manager.pagos_path, index=False)
                                            st.success("✅ Pago visible nuevamente")
                                            st.rerun()
                                        except:
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
    
    # Pestaña 4: Administración
    with tab4:
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
            st.subheader("📦 Agregar Nuevo Producto")
            
            with st.form("form_nuevo_producto"):
                codigo_producto = st.text_input(
                    "🔢 Código del Producto",
                    placeholder="Ej: 2024-001",
                    help="Código único del producto"
                )
                
                nombre_ingles = st.text_input(
                    "🇺🇸 Nombre en Inglés",
                    placeholder="Ej: Brake Pad Set",
                    help="Nombre del producto en inglés"
                )
                
                nombre_espanol = st.text_input(
                    "🇪🇸 Nombre en Español",
                    placeholder="Ej: Pastillas de freno",
                    help="Traducción al español (opcional)"
                )
                
                col_precio, col_peso = st.columns(2)
                
                with col_precio:
                    precio_venta = st.number_input(
                        "💰 Precio de Venta",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        help="Precio de venta en pesos argentinos"
                    )
                
                with col_peso:
                    peso = st.number_input(
                        "⚖️ Peso (kg)",
                        min_value=0.0,
                        step=0.1,
                        format="%.2f",
                        help="Peso del producto en kilogramos (opcional)"
                    )
                
                submit_producto = st.form_submit_button("✅ Agregar Producto", type="primary", use_container_width=True)
                
                if submit_producto:
                    if codigo_producto.strip() and nombre_ingles.strip():
                        success, message = st.session_state.sales_manager.agregar_producto(
                            codigo_producto.strip().upper(),
                            nombre_ingles.strip(),
                            nombre_espanol.strip() if nombre_espanol.strip() else "",
                            precio_venta,
                            peso if peso > 0 else None
                        )
                        
                        if success:
                            st.success(f"✅ {message}")
                            # Recargar datos de productos
                            st.session_state.sales_manager._load_products()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                    else:
                        st.error("❌ El código y nombre en inglés son obligatorios")
            
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