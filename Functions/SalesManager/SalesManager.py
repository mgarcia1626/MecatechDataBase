"""
Sistema de Gestión de Ventas y Pagos para MecatechDataBase.

Este módulo maneja las transacciones de ventas y pagos usando CSV como almacenamiento,
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
    Clase para manejar ventas y pagos en formato CSV.
    """
    
    def __init__(self):
        """Inicializa el gestor de ventas."""
        # Configurar paths
        current_dir = Path(__file__).parent
        base_dir = current_dir.parent.parent
        
        # Archivos de datos
        self.csv_path = base_dir / "DataBase" / "Generated" / "ventas_pagos.csv"
        self.clients_path = base_dir / "DataBase" / "Inputs" / "clientes.json"
        self.products_path = base_dir / "DataBase" / "Generated" / "mecatech_database.json"
        
        # Crear directorio si no existe
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar datos
        self.clients_data = self._load_clients()
        self.products_data = self._load_products()
        
        # Crear CSV si no existe
        self._init_csv()
    
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
    
    def _init_csv(self):
        """Inicializa el archivo CSV con encabezados si no existe."""
        if not self.csv_path.exists():
            headers = [
                'Fecha', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 
                'Precio_Venta', 'Tipo_Operacion', 'Comentarios'
            ]
            
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            
            print(f"✅ Archivo CSV inicializado: {self.csv_path}")
    
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
    
    def add_transaction(self, cliente: str, tipo_operacion: str, 
                       codigo_pieza: str = "", precio_venta: float = None, 
                       comentarios: str = "") -> bool:
        """
        Agrega una nueva transacción al CSV.
        
        Args:
            cliente: Nombre del cliente
            tipo_operacion: 'compra', 'pago', o 'compra-venta'
            codigo_pieza: Código de la pieza (opcional para pagos)
            precio_venta: Precio de venta (se calcula automáticamente si no se proporciona)
            comentarios: Comentarios adicionales
            
        Returns:
            True si se agregó exitosamente, False en caso contrario
        """
        try:
            # Validar cliente
            if not self.validate_client(cliente):
                print(f"❌ Cliente '{cliente}' no existe en la base de datos")
                return False
            
            # Validar código de pieza para compras
            if tipo_operacion in ['compra', 'compra-venta'] and not codigo_pieza:
                print(f"❌ Se requiere código de pieza para operación '{tipo_operacion}'")
                return False
            
            # Variables para la transacción
            nombre_pieza = ""
            precio_final = 0.0
            
            # Procesar según tipo de operación
            if tipo_operacion == 'compra':
                if not self.validate_product_code(codigo_pieza):
                    print(f"❌ Código de pieza '{codigo_pieza}' no existe")
                    return False
                
                nombre_pieza = self.get_product_display_name(codigo_pieza)
                precio_final = precio_venta if precio_venta is not None else self.get_product_sell_price(codigo_pieza)
            
            elif tipo_operacion == 'pago':
                # Para pagos, el precio debe ser negativo
                precio_final = -abs(precio_venta) if precio_venta is not None else 0.0
                nombre_pieza = "PAGO"
            
            elif tipo_operacion == 'compra-venta':
                if not self.validate_product_code(codigo_pieza):
                    print(f"❌ Código de pieza '{codigo_pieza}' no existe")
                    return False
                
                nombre_pieza = self.get_product_display_name(codigo_pieza)
                precio_final = 0.0  # Compra-venta no afecta el total
            
            else:
                print(f"❌ Tipo de operación '{tipo_operacion}' no válido")
                return False
            
            # Crear registro
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            row = [
                fecha_actual,
                cliente,
                codigo_pieza,
                nombre_pieza,
                precio_final,
                tipo_operacion,
                comentarios
            ]
            
            # Agregar al CSV
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            print(f"✅ Transacción agregada: {tipo_operacion} - {cliente} - ${precio_final}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando transacción: {e}")
            return False
    
    def load_transactions(self) -> pd.DataFrame:
        """Carga todas las transacciones desde el CSV."""
        try:
            if self.csv_path.exists():
                df = pd.read_csv(self.csv_path)
                return df
            else:
                return pd.DataFrame(columns=[
                    'Fecha', 'Cliente', 'Codigo_Pieza', 'Nombre_Pieza', 
                    'Precio_Venta', 'Tipo_Operacion', 'Comentarios'
                ])
        except Exception as e:
            print(f"❌ Error cargando transacciones: {e}")
            return pd.DataFrame()
    
    def get_client_balance(self, cliente: str) -> Dict[str, float]:
        """
        Calcula el balance de un cliente específico.
        
        Returns:
            Dict con compras, pagos y balance total
        """
        df = self.load_transactions()
        
        if df.empty:
            return {"compras": 0.0, "pagos": 0.0, "balance": 0.0}
        
        client_transactions = df[df['Cliente'].str.lower() == cliente.lower()]
        
        compras = client_transactions[
            client_transactions['Tipo_Operacion'] == 'compra'
        ]['Precio_Venta'].sum()
        
        pagos = abs(client_transactions[
            client_transactions['Tipo_Operacion'] == 'pago'
        ]['Precio_Venta'].sum())
        
        balance = compras - pagos
        
        return {
            "compras": round(compras, 2),
            "pagos": round(pagos, 2),
            "balance": round(balance, 2)
        }
    
    def get_all_balances(self) -> Dict[str, Dict[str, float]]:
        """Obtiene balances de todos los clientes."""
        df = self.load_transactions()
        
        if df.empty:
            return {}
        
        balances = {}
        for cliente in df['Cliente'].unique():
            balances[cliente] = self.get_client_balance(cliente)
        
        return balances
    
    def get_statistics(self) -> Dict:
        """Obtiene estadísticas generales."""
        df = self.load_transactions()
        
        if df.empty:
            return {
                "total_transactions": 0,
                "total_sales": 0.0,
                "total_payments": 0.0,
                "unique_clients": 0,
                "unique_products": 0
            }
        
        total_sales = df[df['Tipo_Operacion'] == 'compra']['Precio_Venta'].sum()
        total_payments = abs(df[df['Tipo_Operacion'] == 'pago']['Precio_Venta'].sum())
        
        return {
            "total_transactions": len(df),
            "total_sales": round(total_sales, 2),
            "total_payments": round(total_payments, 2),
            "net_balance": round(total_sales - total_payments, 2),
            "unique_clients": df['Cliente'].nunique(),
            "unique_products": df[df['Codigo_Pieza'] != '']['Codigo_Pieza'].nunique()
        }

def main():
    """Función de prueba del sistema."""
    print("🏪 SISTEMA DE GESTIÓN DE VENTAS Y PAGOS")
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
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   Transacciones: {stats['total_transactions']}")
    print(f"   Ventas totales: ${stats['total_sales']}")
    print(f"   Pagos totales: ${stats['total_payments']}")
    
    print(f"\n✅ Sistema inicializado correctamente")

if __name__ == "__main__":
    main()