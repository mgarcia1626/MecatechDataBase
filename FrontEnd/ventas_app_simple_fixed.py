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
            headers = ['Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 'Precio_Unitario', 'Cantidad', 'Precio_Total', 'Estado_Pedido', 'Comentarios']
            with open(self.pedidos_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
    def _init_pagos_csv(self):
        if not self.pagos_path.exists():
            headers = ['Fecha', 'Numero_Pago', 'Cliente', 'Numero_Pedido_Ref', 'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios']
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
                          precio_unitario, cantidad, subtotal, "PENDIENTE", comentarios]
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
            
            row = [fecha_actual, numero_pago, cliente, numero_pedido_ref, codigo_pieza_ref, monto_pago, comentarios]
            
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
    
    def get_client_pedidos(self, cliente):
        """Obtiene todos los pedidos de un cliente específico."""
        df_pedidos = self.load_pedidos()
        if df_pedidos.empty:
            return pd.DataFrame()
        
        return df_pedidos[df_pedidos['Cliente'] == cliente].sort_values('Fecha', ascending=False)
    
    def get_client_pagos(self, cliente):
        """Obtiene todos los pagos de un cliente específico."""
        df_pagos = self.load_pagos()
        if df_pagos.empty:
            return pd.DataFrame()
        
        return df_pagos[df_pagos['Cliente'] == cliente].sort_values('Fecha', ascending=False)
    
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
    tab1, tab2 = st.tabs(["🏪 Operaciones", "📊 Visualización por Cliente"])
    
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
                    
                    # Seleccionar y renombrar columnas para mejor visualización
                    cols_to_show = ['Fecha', 'Numero_Pedido', 'Codigo_Pieza', 'Nombre_Pieza', 'Cantidad', 'Precio_Total', 'Estado_Pedido']
                    df_display_pedidos = df_display_pedidos[cols_to_show]
                    df_display_pedidos.columns = ['Fecha', 'Nº Pedido', 'Código', 'Producto', 'Cant.', 'Total', 'Estado']
                    
                    st.dataframe(
                        df_display_pedidos,
                        use_container_width=True,
                        hide_index=True,
                        height=400
                    )
                    
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
                    
                    # Resumen de pagos
                    total_pagos_count = len(df_pagos)
                    promedio_pago = df_pagos['Monto_Pago'].mean()
                    
                    st.write(f"**📊 Resumen:** {total_pagos_count} pagos total | Promedio: ${promedio_pago:,.2f}")
                    
                else:
                    st.info("📄 No hay pagos registrados para este cliente")
        else:
            st.info("👆 Selecciona un cliente para ver su historial de pedidos y pagos")

if __name__ == "__main__":
    main()