"""
Sistema de Gestión de Ventas y Pagos para MecatechDataBase.

Este módulo maneja las transacciones de ventas y pagos usando CSV separados como almacenamiento,
con validaciones automáticas de clientes y productos.
"""

import csv
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

class SalesManager:
    """
    Clase para manejar ventas y pagos en formatos CSV separados.
    """
    
    def __init__(self):
        """Inicializa el gestor de ventas."""
        # Configurar paths
        current_dir = Path(__file__).parent
        base_dir = current_dir.parent.parent
        
        # Archivos de datos - ahora separados
        self.pedidos_path = base_dir / "DataBase" / "Generated" / "pedidos.csv"
        self.pagos_path = base_dir / "DataBase" / "Generated" / "pagos.csv"
        self.clients_path = base_dir / "DataBase" / "Generated" / "clientes.json"
        self.products_path = base_dir / "DataBase" / "Generated" / "mecatech_database.json"
        
        # Crear directorio si no existe
        self.pedidos_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar datos
        self.clients_data = self._load_clients()
        self.products_data = self._load_products()
        
        # Crear CSVs si no existen
        self._init_pedidos_csv()
        self._init_pagos_csv()
    
    def _load_clients(self) -> Dict:
        """Carga la lista de clientes."""
        try:
            if self.clients_path.exists():
                with open(self.clients_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"clientes": []}
        except Exception as e:
            print(f"❌ Error cargando clientes: {e}")
            return {"clientes": []}
    
    def _load_products(self) -> Dict:
        """Carga la base de datos de productos."""
        try:
            if self.products_path.exists():
                with open(self.products_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Error cargando productos: {e}")
            return {}
    
    def _init_pedidos_csv(self):
        """Inicializa el archivo CSV de pedidos con encabezados si no existe."""
        if not self.pedidos_path.exists():
            headers = [
                'Fecha', 'Numero_Pedido', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 
                'Precio_Unitario', 'Cantidad', 'Precio_Total', 'Estado_Pedido', 'Comentarios', 'EstadoVisualizacion'
            ]
            
            with open(self.pedidos_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print(f"✅ Archivo pedidos.csv inicializado: {self.pedidos_path}")

    def _init_pagos_csv(self):
        """Inicializa el archivo CSV de pagos con encabezados si no existe."""
        if not self.pagos_path.exists():
            headers = [
                'Fecha', 'Numero_Pago', 'Cliente', 'Numero_Pedido_Ref', 
                'Codigo_Pieza_Ref', 'Monto_Pago', 'Comentarios', 'EstadoVisualizacion'
            ]
            
            with open(self.pagos_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print(f"✅ Archivo pagos.csv inicializado: {self.pagos_path}")
    
    def get_client_names(self) -> List[str]:
        """Retorna lista de nombres de clientes disponibles."""
        return [client["nombre"] for client in self.clients_data["clientes"]]
    
    def validate_client(self, client_name: str) -> bool:
        """Valida si el cliente existe."""
        client_names = [c["nombre"].lower() for c in self.clients_data["clientes"]]
        return client_name.lower() in client_names
    
    def validate_product_code(self, code: str) -> bool:
        """Valida si el código de producto existe."""
        return code in self.products_data
    
    def get_product_info(self, code: str) -> Optional[Dict]:
        """Obtiene información de un producto por código."""
        return self.products_data.get(code)
    
    def search_products_by_name(self, search_term: str) -> List[Tuple[str, str, str]]:
        """
        Busca productos por nombre (español o inglés).
        
        Returns:
            Lista de tuplas (código, nombre_español, nombre_inglés)
        """
        results = []
        search_term = search_term.lower()
        
        for code, product in self.products_data.items():
            name_english = product.get('name', '').lower()
            name_spanish = product.get('espanol', '').lower() if product.get('espanol') else ''
            
            # Buscar en ambos nombres
            if (search_term in name_english or 
                search_term in name_spanish or 
                search_term in code.lower()):
                
                display_spanish = product.get('espanol', '')
                display_english = product.get('name', '')
                
                results.append((code, display_spanish, display_english))
        
        return results[:20]  # Limitar a 20 resultados
    
    def get_product_display_name(self, code: str) -> str:
        """
        Obtiene el nombre de display (español preferido, inglés como fallback).
        """
        product = self.get_product_info(code)
        if not product:
            return "Producto no encontrado"
        
        spanish_name = product.get('espanol', '')
        english_name = product.get('name', '')
        
        return spanish_name if spanish_name and spanish_name.strip() else english_name
    
    def get_product_sell_price(self, code: str) -> float:
        """Obtiene el precio de venta de un producto."""
        product = self.get_product_info(code)
        if not product:
            return 0.0
        
        arg_data = product.get('ARG', {})
        return float(arg_data.get('Sell_price', 0.0))

    def _get_next_pedido_number(self) -> str:
        """Genera el siguiente número de pedido."""
        try:
            df = pd.read_csv(self.pedidos_path)
            if df.empty:
                return "PED001"
            
            # Extraer números y encontrar el máximo
            pedido_numbers = df['Numero_Pedido'].str.extract(r'PED(\d+)')[0].astype(int)
            next_num = pedido_numbers.max() + 1
            return f"PED{next_num:03d}"
        except:
            return "PED001"

    def _get_next_pago_number(self) -> str:
        """Genera el siguiente número de pago."""
        try:
            df = pd.read_csv(self.pagos_path)
            if df.empty:
                return "PAG001"
            
            # Extraer números y encontrar el máximo
            pago_numbers = df['Numero_Pago'].str.extract(r'PAG(\d+)')[0].astype(int)
            next_num = pago_numbers.max() + 1
            return f"PAG{next_num:03d}"
        except:
            return "PAG001"

    def load_pedidos(self) -> pd.DataFrame:
        """Carga los pedidos desde el CSV."""
        try:
            if self.pedidos_path.exists():
                return pd.read_csv(self.pedidos_path)
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error cargando pedidos: {e}")
            return pd.DataFrame()

    def load_pagos(self) -> pd.DataFrame:
        """Carga los pagos desde el CSV."""
        try:
            if self.pagos_path.exists():
                return pd.read_csv(self.pagos_path)
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Error cargando pagos: {e}")
            return pd.DataFrame()
    
    def add_pedido(self, cliente: str, codigo_pieza: str, precio_unitario: float, 
                   comentarios: str = "", cantidad: int = 1) -> Tuple[bool, str]:
        """Agrega un nuevo pedido individual."""
        try:
            if not self.validate_client(cliente):
                return False, "Cliente no existe"
            
            if not self.validate_product_code(codigo_pieza):
                return False, "Código de producto no existe"
            
            numero_pedido = self._get_next_pedido_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nombre_pieza = self.get_product_display_name(codigo_pieza)
            precio_total = precio_unitario * cantidad
            
            row = [
                fecha_actual,
                numero_pedido,
                cliente,
                codigo_pieza,
                nombre_pieza,
                precio_unitario,
                cantidad,
                precio_total,
                "Pendiente",
                comentarios,
                "Visible"
            ]
            
            with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pedido
            
        except Exception as e:
            print(f"❌ Error agregando pedido: {e}")
            return False, str(e)

    def add_pedido_multiple(self, cliente: str, items: List[Dict], comentarios: str = "") -> Tuple[bool, str]:
        """Agrega un pedido con múltiples productos."""
        try:
            if not self.validate_client(cliente):
                return False, "Cliente no existe"
            
            numero_pedido = self._get_next_pedido_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            rows = []
            for item in items:
                codigo_pieza = item['codigo']
                cantidad = item['cantidad']
                precio_unitario = item['precio_unitario']
                
                if not self.validate_product_code(codigo_pieza):
                    continue
                
                nombre_pieza = self.get_product_display_name(codigo_pieza)
                precio_total = precio_unitario * cantidad
                
                rows.append([
                    fecha_actual,
                    numero_pedido,
                    cliente,
                    codigo_pieza,
                    nombre_pieza,
                    precio_unitario,
                    cantidad,
                    precio_total,
                    "Pendiente",
                    comentarios,
                    "Visible"
                ])
            
            if not rows:
                return False, "No hay productos válidos"
            
            with open(self.pedidos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in rows:
                    writer.writerow(row)
            
            return True, numero_pedido
            
        except Exception as e:
            print(f"❌ Error agregando pedido múltiple: {e}")
            return False, str(e)

    def add_pago(self, cliente: str, monto: float, numero_pedido_ref: str = "", 
                 codigo_pieza_ref: str = "", comentarios: str = "") -> Tuple[bool, str]:
        """Agrega un nuevo pago."""
        try:
            if not self.validate_client(cliente):
                return False, "Cliente no existe"
            
            numero_pago = self._get_next_pago_number()
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row = [
                fecha_actual,
                numero_pago,
                cliente,
                numero_pedido_ref,
                codigo_pieza_ref,
                monto,
                comentarios,
                "Visible"
            ]
            
            with open(self.pagos_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            return True, numero_pago
            
        except Exception as e:
            print(f"❌ Error agregando pago: {e}")
            return False, str(e)

    def add_pago_inmediato(self, cliente: str, items: List[Dict], comentarios: str = "") -> Tuple[bool, str, str]:
        """Crea un pedido y lo paga inmediatamente."""
        try:
            # Crear pedido primero
            success_pedido, numero_pedido = self.add_pedido_multiple(cliente, items, comentarios)
            
            if not success_pedido:
                return False, "", ""
            
            # Calcular total del pedido
            total_pedido = sum(item['precio_unitario'] * item['cantidad'] for item in items)
            
            # Crear pago
            success_pago, numero_pago = self.add_pago(
                cliente, 
                total_pedido, 
                numero_pedido, 
                items[0]['codigo'] if items else "",
                f"Pago inmediato - {comentarios}"
            )
            
            if success_pago:
                return True, numero_pedido, numero_pago
            else:
                return False, numero_pedido, ""
                
        except Exception as e:
            print(f"❌ Error en pago inmediato: {e}")
            return False, "", str(e)
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas generales del nuevo sistema."""
        df_pedidos = self.load_pedidos()
        df_pagos = self.load_pagos()
        
        total_pedidos = len(df_pedidos) if not df_pedidos.empty else 0
        total_pagos = len(df_pagos) if not df_pagos.empty else 0
        total_sales = df_pedidos['Precio_Total'].sum() if not df_pedidos.empty else 0.0
        total_payments = df_pagos['Monto_Pago'].sum() if not df_pagos.empty else 0.0
        
        unique_clients_pedidos = df_pedidos['Cliente'].nunique() if not df_pedidos.empty else 0
        unique_clients_pagos = df_pagos['Cliente'].nunique() if not df_pagos.empty else 0
        unique_clients = max(unique_clients_pedidos, unique_clients_pagos)
        
        return {
            "total_transactions": total_pedidos + total_pagos,
            "total_pedidos": total_pedidos,
            "total_pagos": total_pagos,
            "total_sales": round(total_sales, 2),
            "total_payments": round(total_payments, 2),
            "net_balance": round(total_sales - total_payments, 2),
            "unique_clients": unique_clients,
            "unique_products": df_pedidos['Codigo_Pieza'].nunique() if not df_pedidos.empty else 0
        }
    
    def get_client_pedidos(self, cliente: str, incluir_ocultos: bool = False) -> pd.DataFrame:
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
    
    def get_client_pagos(self, cliente: str, incluir_ocultos: bool = False) -> pd.DataFrame:
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
    
    def get_client_balance(self, cliente: str) -> Dict[str, float]:
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
    
    def ocultar_pedido(self, numero_pedido: str) -> bool:
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
    
    def ocultar_pago(self, numero_pago: str) -> bool:
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
    
    def eliminar_pedido(self, numero_pedido: str) -> bool:
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
    
    def eliminar_pago(self, numero_pago: str) -> bool:
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

def main():
    """Función de prueba del sistema."""
    print("🏪 SISTEMA DE GESTIÓN DE PEDIDOS Y PAGOS (V2)")
    print("=" * 50)
    
    # Crear instancia
    sales_manager = SalesManager()
    
    print(f"\n📊 Clientes disponibles: {len(sales_manager.get_client_names())}")
    print(f"📦 Productos disponibles: {len(sales_manager.products_data)}")
    
    # Mostrar algunos clientes
    print(f"\n👥 Primeros 5 clientes:")
    for i, client in enumerate(sales_manager.get_client_names()[:5], 1):
        print(f"   {i}. {client}")
    
    # Ejemplo de búsqueda de productos
    print(f"\n🔍 Búsqueda 'brake':")
    results = sales_manager.search_products_by_name("brake")
    for code, spanish, english in results[:3]:
        print(f"   {code}: {spanish or english}")
    
    # Mostrar estadísticas
    stats = sales_manager.get_statistics()
    print(f"\n📈 ESTADÍSTICAS DEL NUEVO SISTEMA:")
    print(f"   Total transacciones: {stats['total_transactions']}")
    print(f"   Total pedidos: {stats['total_pedidos']}")
    print(f"   Total pagos: {stats['total_pagos']}")
    print(f"   Ventas totales: ${stats['total_sales']}")
    print(f"   Pagos totales: ${stats['total_payments']}")
    print(f"   Balance neto: ${stats['net_balance']}")
    
    print(f"\n✅ Sistema de pedidos y pagos inicializado correctamente")

if __name__ == "__main__":
    main()