"""
Aplicación Streamlit para Gestión de Ventas y Pagos - MecatechDataBase.

Interfaz web para registrar transacciones, consultar balances y 
visualizar estadísticas de ventas y pagos.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

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

# Crear clase SalesManager simplificada (sin importación externa)
import csv
import json
from datetime import datetime

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
            headers = ['Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 'Precio_Venta', 'Estado_Pedido', 'Comentarios']
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
        if 'Numero_Pedido' in df.columns:
            pedidos = df['Numero_Pedido'].dropna()
            if not pedidos.empty:
                # Extraer números de los pedidos existentes
                numeros = []
                for pedido in pedidos:
                    if isinstance(pedido, str) and pedido.startswith('PED'):
                        try:
                            num = int(pedido[3:])
                            numeros.append(num)
                        except:
                            continue
                
                if numeros:
                    siguiente_num = max(numeros) + 1
                    return f"PED{siguiente_num:03d}"
        
        return "PED001"
    
    def add_pedido(self, cliente, codigo_pieza, precio_venta=None, comentarios="", numero_pedido=None):
        """Agrega un pedido al CSV de pedidos."""
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if numero_pedido is None:
                numero_pedido = self.generate_pedido_number()
            
            product = self.products_data.get(codigo_pieza, {})
            spanish_name = product.get('espanol', '')
            english_name = product.get('name', '')
            nombre_pieza = spanish_name if spanish_name else english_name
            
            if precio_venta is None:
                precio_final = self.get_product_sell_price(codigo_pieza)
            else:
                precio_final = precio_venta
            
            row = [fecha_actual, numero_pedido, cliente, codigo_pieza, nombre_pieza, precio_final, 'PENDIENTE', comentarios]
            
            with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pedido
        except Exception as e:
            st.error(f"Error al agregar pedido: {e}")
            return False, None
    
    def add_pago(self, cliente, monto_pago, numero_pedido_ref="", codigo_pieza_ref="", comentarios="", numero_pago=None):
        """Agrega un pago al CSV de pagos."""
        try:
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if numero_pago is None:
                numero_pago = self.generate_pago_number()
            
            row = [fecha_actual, numero_pago, cliente, numero_pedido_ref, codigo_pieza_ref, monto_pago, comentarios]
            
            with open(self.pagos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pago
        except Exception as e:
            st.error(f"Error al agregar pago: {e}")
            return False, None
    
    def add_pago_inmediato(self, cliente, codigo_pieza, precio_venta=None, comentarios=""):
        """Agrega un pedido y su pago inmediatamente."""
        try:
            # Primero crear el pedido
            success_pedido, numero_pedido = self.add_pedido(cliente, codigo_pieza, precio_venta, comentarios)
            
            if success_pedido:
                # Luego crear el pago asociado
                precio_final = precio_venta if precio_venta is not None else self.get_product_sell_price(codigo_pieza)
                comentarios_pago = f"Pago inmediato para pedido {numero_pedido}"
                if comentarios:
                    comentarios_pago += f" - {comentarios}"
                
                success_pago, numero_pago = self.add_pago(cliente, precio_final, numero_pedido, codigo_pieza, comentarios_pago)
                
                if success_pago:
                    # Actualizar estado del pedido a PAGADO
                    self.update_pedido_estado(numero_pedido, 'PAGADO')
                    return True, numero_pedido, numero_pago
                
            return False, None, None
        except Exception as e:
            st.error(f"Error en pago inmediato: {e}")
            return False, None, None
    
    def update_pedido_estado(self, numero_pedido, nuevo_estado):
        """Actualiza el estado de un pedido."""
        try:
            df = self.load_pedidos()
            if not df.empty:
                df.loc[df['Numero_Pedido'] == numero_pedido, 'Estado_Pedido'] = nuevo_estado
                df.to_csv(self.pedidos_path, index=False)
                return True
        except Exception as e:
            st.error(f"Error al actualizar estado: {e}")
        return False
    
    def load_pedidos(self):
        try:
            if self.pedidos_path.exists():
                return pd.read_csv(self.pedidos_path)
            else:
                return pd.DataFrame(columns=['Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 'Precio_Venta', 'Estado_Pedido', 'Comentarios'])
        except:
            return pd.DataFrame()
    
    def load_pagos(self):
        try:
            if self.pagos_path.exists():
                return pd.read_csv(self.pagos_path)
            else:
                return pd.DataFrame(columns=['Fecha', 'Numero_Pago', 'Cliente', 'Numero_Pedido_Ref', 'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios'])
        except:
            return pd.DataFrame()
    
    def get_all_balances(self):
        df_pedidos = self.load_pedidos()
        df_pagos = self.load_pagos()
        
        if df_pedidos.empty and df_pagos.empty:
            return {}
        
        balances = {}
        
        # Obtener todos los clientes únicos
        clientes_pedidos = set(df_pedidos['Cliente'].unique()) if not df_pedidos.empty else set()
        clientes_pagos = set(df_pagos['Cliente'].unique()) if not df_pagos.empty else set()
        all_clients = clientes_pedidos.union(clientes_pagos)
        
        for cliente in all_clients:
            # Calcular total de pedidos
            pedidos_cliente = df_pedidos[df_pedidos['Cliente'] == cliente]['Precio_Venta'].sum() if not df_pedidos.empty else 0
            
            # Calcular total de pagos
            pagos_cliente = df_pagos[df_pagos['Cliente'] == cliente]['Monto_Pago'].sum() if not df_pagos.empty else 0
            
            balance = pedidos_cliente - pagos_cliente
            
            balances[cliente] = {
                "pedidos": round(pedidos_cliente, 2),
                "pagos": round(pagos_cliente, 2),
                "balance": round(balance, 2)
            }
        return balances
    
    def get_statistics(self):
        df_pedidos = self.load_pedidos()
        df_pagos = self.load_pagos()
        
        total_pedidos = len(df_pedidos) if not df_pedidos.empty else 0
        total_pagos_count = len(df_pagos) if not df_pagos.empty else 0
        total_transactions = total_pedidos + total_pagos_count
        
        total_sales = df_pedidos['Precio_Venta'].sum() if not df_pedidos.empty else 0.0
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

def init_session_state():
    """Inicializa variables de estado de sesión."""
    if 'sales_manager' not in st.session_state:
        st.session_state.sales_manager = SalesManager()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = None

def search_products(search_term):
    """Busca productos y actualiza los resultados."""
    if search_term:
        results = st.session_state.sales_manager.search_products_by_name(search_term)
        st.session_state.search_results = results
    else:
        st.session_state.search_results = []

def main():
    st.set_page_config(
        page_title="Ventas y Pagos - MecatechDataBase",
        page_icon="🏪",
        layout="wide"
    )
    
    # Inicializar estado
    init_session_state()
    
    st.title("🏪 Sistema de Ventas y Pagos")
    st.markdown("---")
    
    # Sidebar con estadísticas
    with st.sidebar:
        st.subheader("📊 Estadísticas Generales")
        stats = st.session_state.sales_manager.get_statistics()
        
        st.metric("📝 Total Transacciones", stats['total_transactions'])
        st.metric("💰 Ventas Totales", f"${stats['total_sales']:,.2f}")
        st.metric("💵 Pagos Totales", f"${stats['total_payments']:,.2f}")
        st.metric("⚖️ Balance Neto", f"${stats['net_balance']:,.2f}")
        st.metric("👥 Clientes Únicos", stats['unique_clients'])
        st.metric("📦 Productos Únicos", stats['unique_products'])
    
    # Interfaz principal simplificada
    
    with tab1:
        st.subheader("🛒 Registrar Nuevo Pedido")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Selección de cliente
            clientes = st.session_state.sales_manager.get_client_names()
            cliente_seleccionado = st.selectbox(
                "👤 Cliente",
                options=[""] + clientes,
                key="cliente_select"
            )
            
            # Tipo de operación
            tipo_operacion = st.selectbox(
                "🔄 Tipo de Operación",
                options=["", "compra", "pago", "compra-venta"],
                key="tipo_select"
            )
            
            # Comentarios
            comentarios = st.text_area(
                "💬 Comentarios",
                key="comentarios_input",
                height=80
            )
        
        with col2:
            if tipo_operacion in ["compra", "compra-venta"]:
                st.write("**🔍 Buscar Producto**")
                
                # Búsqueda de producto
                col2a, col2b = st.columns([3, 1])
                
                with col2a:
                    search_term = st.text_input(
                        "Buscar por código o nombre",
                        placeholder="Ej: brake, 1234, pedal...",
                        key="product_search"
                    )
                
                with col2b:
                    if st.button("🔍 Buscar", key="search_btn"):
                        search_products(search_term)
                
                # Mostrar resultados de búsqueda
                if st.session_state.search_results:
                    st.write("**📋 Resultados de Búsqueda:**")
                    
                    for i, (code, spanish, english) in enumerate(st.session_state.search_results):
                        display_name = spanish if spanish else english
                        
                        col_code, col_name, col_select = st.columns([1, 3, 1])
                        
                        with col_code:
                            st.text(code)
                        
                        with col_name:
                            st.text(display_name[:40] + "..." if len(display_name) > 40 else display_name)
                        
                        with col_select:
                            if st.button("Seleccionar", key=f"select_{i}"):
                                st.session_state.selected_product = {
                                    'code': code,
                                    'name': display_name
                                }
                                st.rerun()
                
                # Mostrar producto seleccionado
                if st.session_state.selected_product:
                    st.success(f"✅ **Producto Seleccionado:**")
                    st.write(f"**Código:** {st.session_state.selected_product['code']}")
                    st.write(f"**Nombre:** {st.session_state.selected_product['name']}")
                    
                    # Obtener precio automático
                    precio_auto = st.session_state.sales_manager.get_product_sell_price(
                        st.session_state.selected_product['code']
                    )
                    st.write(f"**Precio Sugerido:** ${precio_auto:,.2f}")
                    
                    if st.button("🗑️ Limpiar Selección", key="clear_selection"):
                        st.session_state.selected_product = None
                        st.rerun()
            
            elif tipo_operacion == "pago":
                st.write("**💵 Información de Pago**")
                st.info("Para pagos, no se requiere seleccionar producto.")
        
        # Formulario de transacción
        st.markdown("---")
        st.subheader("📝 Confirmar Transacción")
        
        # Campo para número de pedido personalizado
        col_pedido1, col_pedido2 = st.columns([1, 3])
        with col_pedido1:
            usar_numero_personalizado = st.checkbox("📋 Número de pedido personalizado", key="custom_order_check")
        with col_pedido2:
            if usar_numero_personalizado:
                numero_pedido_personalizado = st.text_input(
                    "Número de pedido", 
                    placeholder="Ej: PED-2025-001",
                    key="custom_order_input"
                )
            else:
                numero_pedido_personalizado = None
                st.info("Se generará automáticamente (Ej: PED001, PED002...)")
        
        col3, col4, col5 = st.columns([2, 2, 1])
        
        with col3:
            # Campo de código (editable o automático)
            if st.session_state.selected_product:
                codigo_pieza = st.text_input(
                    "🏷️ Código de Pieza",
                    value=st.session_state.selected_product['code'],
                    disabled=(tipo_operacion == "pago"),
                    key="codigo_input"
                )
            else:
                codigo_pieza = st.text_input(
                    "🏷️ Código de Pieza",
                    placeholder="Ej: ABC123" if tipo_operacion != "pago" else "No requerido",
                    disabled=(tipo_operacion == "pago"),
                    key="codigo_manual"
                )
        
        with col4:
            # Campo de precio
            precio_placeholder = 0.0
            if st.session_state.selected_product and tipo_operacion != "compra-venta":
                precio_placeholder = st.session_state.sales_manager.get_product_sell_price(
                    st.session_state.selected_product['code']
                )
            
            if tipo_operacion == "compra-venta":
                st.text_input("💰 Precio", value="$0.00 (No afecta balance)", disabled=True)
                precio_venta = 0.0
            else:
                precio_venta = st.number_input(
                    "💰 Precio",
                    min_value=0.0,
                    value=float(precio_placeholder),
                    step=0.01,
                    format="%.2f",
                    key="precio_input"
                )
        
        with col5:
            st.write("")
            st.write("")
            if st.button("✅ Registrar", key="register_btn", type="primary"):
                # Validaciones
                if not cliente_seleccionado:
                    st.error("❌ Debe seleccionar un cliente")
                elif not tipo_operacion:
                    st.error("❌ Debe seleccionar un tipo de operación")
                elif tipo_operacion in ["compra", "compra-venta"] and not codigo_pieza:
                    st.error("❌ Debe especificar un código de pieza")
                elif tipo_operacion == "pago" and precio_venta <= 0:
                    st.error("❌ El monto del pago debe ser mayor a 0")
                else:
                    # Registrar transacción
                    success, numero_pedido_generado = st.session_state.sales_manager.add_transaction(
                        cliente=cliente_seleccionado,
                        tipo_operacion=tipo_operacion,
                        codigo_pieza=codigo_pieza,
                        precio_venta=precio_venta,
                        comentarios=comentarios,
                        numero_pedido=numero_pedido_personalizado
                    )
                    
                    if success:
                        if tipo_operacion == 'compra-venta':
                            st.success(f"✅ Transacción registrada exitosamente")
                            st.info(f"📋 Número de pedido: **{numero_pedido_generado}** - Pago asociado a este pedido")
                        else:
                            st.success(f"✅ Transacción registrada exitosamente - Pedido: **{numero_pedido_generado}**")
                        # Limpiar formulario
                        st.session_state.selected_product = None
                        st.session_state.search_results = []
                        st.rerun()
                    else:
                        st.error("❌ Error al registrar la transacción")
    
    with tab2:
        st.subheader("📋 Historial de Transacciones")
        
        # Cargar transacciones
        df = st.session_state.sales_manager.load_transactions()
        
        if not df.empty:
            # Filtros
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cliente_filter = st.selectbox(
                    "Filtrar por Cliente",
                    options=["Todos"] + list(df['Cliente'].unique()),
                    key="cliente_filter"
                )
            
            with col2:
                tipo_filter = st.selectbox(
                    "Filtrar por Tipo",
                    options=["Todos"] + list(df['Tipo_Operacion'].unique()),
                    key="tipo_filter"
                )
            
            with col3:
                fecha_filter = st.date_input(
                    "Desde Fecha",
                    value=None,
                    key="fecha_filter"
                )
            
            # Aplicar filtros
            df_filtered = df.copy()
            
            if cliente_filter != "Todos":
                df_filtered = df_filtered[df_filtered['Cliente'] == cliente_filter]
            
            if tipo_filter != "Todos":
                df_filtered = df_filtered[df_filtered['Tipo_Operacion'] == tipo_filter]
            
            if fecha_filter:
                df_filtered['Fecha'] = pd.to_datetime(df_filtered['Fecha'])
                df_filtered = df_filtered[df_filtered['Fecha'].dt.date >= fecha_filter]
            
            # Mostrar tabla
            st.dataframe(
                df_filtered,
                use_container_width=True,
                column_config={
                    "Fecha": st.column_config.DatetimeColumn("Fecha", format="DD/MM/YYYY HH:mm"),
                    "Precio_Venta": st.column_config.NumberColumn("Precio", format="$%.2f"),
                    "Numero_Pedido": st.column_config.TextColumn("Nº Pedido", width="small"),
                }
            )
            
            # Descargar CSV
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"transacciones_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        else:
            st.info("📝 No hay transacciones registradas aún")
    
    with tab3:
        st.subheader("💰 Balances por Cliente")
        
        # Obtener todos los balances
        balances = st.session_state.sales_manager.get_all_balances()
        
        if balances:
            # Convertir a DataFrame para mejor visualización
            balance_data = []
            for cliente, data in balances.items():
                balance_data.append({
                    'Cliente': cliente,
                    'Compras': data['compras'],
                    'Pagos': data['pagos'],
                    'Balance': data['balance']
                })
            
            df_balances = pd.DataFrame(balance_data)
            
            # Ordenar por balance descendente
            df_balances = df_balances.sort_values('Balance', ascending=False)
            
            st.dataframe(
                df_balances,
                use_container_width=True,
                column_config={
                    "Compras": st.column_config.NumberColumn("Compras", format="$%.2f"),
                    "Pagos": st.column_config.NumberColumn("Pagos", format="$%.2f"),
                    "Balance": st.column_config.NumberColumn("Balance", format="$%.2f"),
                }
            )
            
            # Resumen
            st.subheader("📊 Resumen de Balances")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_compras = df_balances['Compras'].sum()
                st.metric("Total Compras", f"${total_compras:,.2f}")
            
            with col2:
                total_pagos = df_balances['Pagos'].sum()
                st.metric("Total Pagos", f"${total_pagos:,.2f}")
            
            with col3:
                balance_general = total_compras - total_pagos
                st.metric("Balance General", f"${balance_general:,.2f}")
        
        else:
            st.info("💰 No hay balances para mostrar")
    
    with tab4:
        st.subheader("🔍 Búsqueda de Productos")
        
        search_product = st.text_input(
            "Buscar productos por código o nombre",
            placeholder="Ej: brake, 1234, pedal, freno...",
            key="product_search_tab"
        )
        
        if search_product:
            results = st.session_state.sales_manager.search_products_by_name(search_product)
            
            if results:
                st.write(f"**Encontrados {len(results)} productos:**")
                
                # Crear DataFrame para mejor visualización
                product_data = []
                for code, spanish, english in results:
                    # Obtener precio
                    price = st.session_state.sales_manager.get_product_sell_price(code)
                    
                    product_data.append({
                        'Código': code,
                        'Nombre Español': spanish or 'N/A',
                        'Nombre Inglés': english or 'N/A',
                        'Precio Venta': price
                    })
                
                df_products = pd.DataFrame(product_data)
                
                st.dataframe(
                    df_products,
                    use_container_width=True,
                    column_config={
                        "Precio Venta": st.column_config.NumberColumn("Precio Venta", format="$%.2f"),
                    }
                )
            
            else:
                st.info(f"No se encontraron productos que coincidan con '{search_product}'")

if __name__ == "__main__":
    main()