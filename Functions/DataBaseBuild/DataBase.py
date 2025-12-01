"""
Sistema de Base de Datos para MecatechDataBase.

Este módulo maneja la estructura de datos de piezas con códigos y características,
aplicando los cálculos de precios según las variables de entorno.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from .env_loader import ENV
except ImportError:
    from env_loader import ENV

class MecatechDatabase:
    """
    Clase principal para manejar la base de datos de piezas.
    """
    
    def __init__(self):
        """Inicializa la base de datos."""
        self.pieces_data = {}
        self.weights_data = {}  # Diccionario para almacenar pesos por código
        self.data_path = Path(__file__).parent.parent.parent / "DataBase" / "Inputs" / "PriceList.xlsx"
        
    def calculate_usa_costs(self, dealer_price: float) -> Dict[str, float]:
        """
        Calcula los costos en USA según las fórmulas especificadas.
        
        Fórmulas:
        - total_in_usa = dealer_price * (1 + USATax + shipping_Tax)
        - cost_in_usa_usd = total_in_usa * EuToUsd  
        - final_cost_usa = cost_in_usa_usd * (1 + Victor_Earn)
        
        Args:
            dealer_price: Precio del distribuidor
            
        Returns:
            Dict con los costos calculados
        """
        # Obtener variables del .env
        usa_tax = ENV.get('USATax', 0.17)
        shipping_tax = ENV.get('shipping_Tax', 0.12)
        eu_to_usd = ENV.get('EuToUsd', 1.15)
        victor_earn = ENV.get('Victor_Earn', 0.10)
        
        # Aplicar fórmulas
        total_in_usa = dealer_price * (1 + usa_tax + shipping_tax)
        cost_in_usa_usd = total_in_usa * eu_to_usd
        final_cost_usa = cost_in_usa_usd * (1 + victor_earn)
        
        return {
            'total_in_usa': round(total_in_usa, 2),
            'cost_in_usa_usd': round(cost_in_usa_usd, 2), 
            'final_cost_usa': round(final_cost_usa, 2)
        }
    
    def load_weights_data(self) -> Dict[str, float]:
        """
        Carga los datos de peso desde la hoja 'Weights'.
        
        Returns:
            Dict con código de pieza como clave y peso en gramos como valor
        """
        try:
            df_weights = pd.read_excel(self.data_path, sheet_name='Weights')
            print(f"✅ Cargando pesos desde hoja: Weights")
            print(f"📊 Registros de peso encontrados: {len(df_weights)}")
            
            weights_dict = {}
            for index, row in df_weights.iterrows():
                code = str(row['CODE']).strip()
                weight = row['Peso en gr']
                
                if code and code != 'nan' and not pd.isna(code):
                    if pd.isna(weight) or weight == 0:
                        weights_dict[code] = None  # Sin peso definido
                    else:
                        weights_dict[code] = float(weight)
            
            self.weights_data = weights_dict
            print(f"📦 Pesos cargados para {len(weights_dict)} códigos")
            return weights_dict
            
        except Exception as e:
            print(f"❌ Error cargando pesos: {e}")
            return {}
    
    def calculate_shipping_cost(self, weight_grams: float = None) -> float:
        """
        Calcula el costo de envío basado en el peso.
        
        Fórmula: shipping_cost = weight * DEFAULT_SHIPPING_COST_kg / 1000
        Si no hay peso, usa NO_WHEIGHT_Cost
        
        Args:
            weight_grams: Peso en gramos
            
        Returns:
            Costo de envío calculado
        """
        if weight_grams is None or pd.isna(weight_grams):
            # Usar costo por defecto cuando no hay peso
            no_weight_cost = ENV.get('NO_WHEIGHT_Cost', 5.0)
            return round(float(no_weight_cost), 2)
        
        # Calcular costo basado en peso
        default_shipping_cost_kg = ENV.get('DEFAULT_SHIPPING_COST_kg', 50.0)
        shipping_cost = (float(weight_grams) * float(default_shipping_cost_kg)) / 1000
        return round(shipping_cost, 2)
    
    def calculate_costo_in_arg(self, shipping_cost: float, final_cost_usa: float) -> float:
        """
        Calcula el costo total en Argentina.
        
        Fórmula: Costo_In_Arg = shipping_cost + final_cost_usa
        
        Args:
            shipping_cost: Costo de envío
            final_cost_usa: Costo final en USA
            
        Returns:
            Costo total en Argentina
        """
        return round(float(shipping_cost) + float(final_cost_usa), 2)
    
    def calculate_ref_price(self, code: str, consumer_price: float) -> float:
        """
        Calcula el precio de referencia basado en el código de pieza.
        
        Fórmulas:
        - Códigos normales: Ref_Price = consumer_price * EuToUsd
        - Códigos que empiecen con "1000": Ref_Price = consumer_price * EuToUsd * (1 + BrakeExtra)
        
        Args:
            code: Código de la pieza
            consumer_price: Precio al consumidor
            
        Returns:
            Precio de referencia calculado
        """
        eu_to_usd = ENV.get('EuToUsd', 1.15)
        brake_extra = ENV.get('BrakeExtra', 0.2)
        
        # Calcular precio base
        ref_price = consumer_price * eu_to_usd
        
        # Aplicar factor extra para códigos que empiecen con "1000"
        if code.startswith("1000"):
            ref_price = ref_price * (1 + brake_extra)
        
        return round(ref_price, 2)
    
    def calculate_sell_price(self, costo_in_arg: float) -> float:
        """
        Calcula el precio de venta basado en el costo en Argentina.
        
        Fórmula: Sell_price = Costo_In_Arg * DEFAULT_PROFIT_MARGIN
        
        Args:
            costo_in_arg: Costo total en Argentina
            
        Returns:
            Precio de venta calculado
        """
        default_profit_margin = ENV.get('DEFAULT_PROFIT_MARGIN', 25.0)
        # Convertir porcentaje a decimal (25.0 -> 1.25)
        margin_multiplier = 1 + (default_profit_margin / 100)
        sell_price = costo_in_arg * margin_multiplier
        return round(sell_price, 2)
    
    def calculate_reference_percent(self, sell_price: float, ref_price: float) -> float:
        """
        Calcula el porcentaje de referencia comparando precio de venta vs precio de referencia.
        
        Fórmula: Reference_percent = (Sell_price / Ref_Price) * 100
        
        Args:
            sell_price: Precio de venta
            ref_price: Precio de referencia
            
        Returns:
            Porcentaje de referencia calculado
        """
        if ref_price == 0:
            return 0.0  # Evitar división por cero
        
        reference_percent = ((sell_price / ref_price) - 1)*100
        return round(reference_percent, 2)
    
    def create_piece_entry(self, code: str, name: str, dealer_price: float, 
                          consumer_price: float, espanol: str = None, 
                          qty_for_bag: int = 1, weight_grams: float = None) -> Dict[str, Any]:
        """
        Crea una entrada completa para una pieza.
        
        Args:
            code: Código de la pieza
            name: Nombre en inglés
            dealer_price: Precio del distribuidor
            consumer_price: Precio al consumidor
            espanol: Nombre en español (opcional)
            qty_for_bag: Cantidad por bolsa
            weight_grams: Peso en gramos (opcional, se busca en weights_data si no se proporciona)
            
        Returns:
            Dict con la estructura completa de la pieza
        """
        # Calcular costos en USA
        usa_costs = self.calculate_usa_costs(dealer_price)
        
        # Obtener peso si no se proporcionó
        if weight_grams is None:
            weight_grams = self.weights_data.get(code)
        
        # Calcular costo de envío
        shipping_cost = self.calculate_shipping_cost(weight_grams)
        
        # Calcular costo total en Argentina
        costo_in_arg = self.calculate_costo_in_arg(shipping_cost, usa_costs['final_cost_usa'])
        
        # Calcular precio de referencia
        ref_price = self.calculate_ref_price(code, consumer_price)
        
        # Calcular precio de venta
        sell_price = self.calculate_sell_price(costo_in_arg)
        
        # Calcular porcentaje de referencia
        reference_percent = self.calculate_reference_percent(sell_price, ref_price)
        
        # Crear estructura completa con sección ARG separada
        piece_data = {
            "name": name,
            "espanol": espanol,
            "qty_for_bag": qty_for_bag,
            "dealer_price": dealer_price,
            "consumer_price": consumer_price,
            **usa_costs,
            "ARG": {
                "weight": weight_grams,
                "shipping_cost": shipping_cost,
                "Costo_In_Arg": costo_in_arg,
                "Ref_Price": ref_price,
                "Sell_price": sell_price,
                "Reference_percent": reference_percent
            }
        }
        
        return piece_data
    
    def load_from_excel(self, sheet_name: str = "CostoUSA") -> Dict[str, Dict[str, Any]]:
        """
        Carga datos desde el archivo Excel y crea la estructura de base de datos.
        
        Args:
            sheet_name: Nombre de la hoja a cargar (por defecto "CostoUSA")
            
        Returns:
            Dict con la estructura completa de la base de datos
        """
        try:
            # Primero cargar los datos de peso
            self.load_weights_data()
            
            # Cargar datos del Excel
            df = pd.read_excel(self.data_path, sheet_name=sheet_name)
            print(f"✅ Cargando datos de hoja: {sheet_name}")
            print(f"📊 Filas encontradas: {len(df)}")
            
            # Mapear columnas (ajustar según la estructura real del Excel CostoUSA)
            column_mapping = {
                'CODE': 'code',
                'Name': 'name',
                'Español': 'espanol',
                'Q.TY FOR BAG': 'qty_for_bag',
                'DEALER': 'dealer_price',
                'CONSUMER': 'consumer_price',
                'Total in USA': 'total_in_usa',
                'Cost in USA (usd)': 'cost_in_usa_usd',
                'Final Cost in USA': 'final_cost_usa'
            }
            
            # Identificar columnas disponibles
            available_cols = df.columns.tolist()
            print(f"🔍 Columnas disponibles: {available_cols}")
            
            # Mapear columnas encontradas
            mapped_cols = {}
            for excel_col in available_cols:
                for pattern, target in column_mapping.items():
                    if pattern.lower() in excel_col.lower():
                        mapped_cols[target] = excel_col
                        break
            
            print(f"🗺️ Columnas mapeadas: {mapped_cols}")
            
            database = {}
            processed = 0
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Extraer código (campo obligatorio)
                    code = None
                    if 'code' in mapped_cols:
                        code = str(row[mapped_cols['code']]).strip()
                    
                    if not code or code == 'nan' or pd.isna(code):
                        continue
                    
                    # Extraer campos principales
                    name = row[mapped_cols.get('name', available_cols[1])] if 'name' in mapped_cols else "Sin nombre"
                    dealer_price = row[mapped_cols.get('dealer_price', available_cols[4])] if 'dealer_price' in mapped_cols else 0.0
                    consumer_price = row[mapped_cols.get('consumer_price', available_cols[5])] if 'consumer_price' in mapped_cols else 0.0
                    
                    # Campos opcionales
                    espanol = row[mapped_cols['espanol']] if 'espanol' in mapped_cols else None
                    qty_for_bag = int(row[mapped_cols['qty_for_bag']]) if 'qty_for_bag' in mapped_cols else 1
                    
                    # Validar precios
                    if pd.isna(dealer_price) or dealer_price <= 0:
                        print(f"⚠️ Precio dealer inválido para {code}: {dealer_price}")
                        continue
                    
                    if pd.isna(consumer_price):
                        consumer_price = 0.0
                    
                    # Obtener valores calculados del Excel si están disponibles
                    total_in_usa = row[mapped_cols['total_in_usa']] if 'total_in_usa' in mapped_cols and not pd.isna(row[mapped_cols['total_in_usa']]) else None
                    cost_in_usa_usd = row[mapped_cols['cost_in_usa_usd']] if 'cost_in_usa_usd' in mapped_cols and not pd.isna(row[mapped_cols['cost_in_usa_usd']]) else None
                    final_cost_usa = row[mapped_cols['final_cost_usa']] if 'final_cost_usa' in mapped_cols and not pd.isna(row[mapped_cols['final_cost_usa']]) else None
                    
                    # Obtener peso para esta pieza
                    weight_grams = self.weights_data.get(code)
                    shipping_cost = self.calculate_shipping_cost(weight_grams)
                    
                    # Si los valores ya están calculados en el Excel, usarlos; si no, calcularlos
                    if total_in_usa is not None and cost_in_usa_usd is not None and final_cost_usa is not None:
                        # Calcular costo total en Argentina
                        final_cost_value = round(float(final_cost_usa), 2)
                        costo_in_arg = self.calculate_costo_in_arg(shipping_cost, final_cost_value)
                        
                        # Calcular precio de referencia
                        ref_price = self.calculate_ref_price(code, float(consumer_price))
                        
                        # Calcular precio de venta
                        sell_price = self.calculate_sell_price(costo_in_arg)
                        
                        # Calcular porcentaje de referencia
                        reference_percent = self.calculate_reference_percent(sell_price, ref_price)
                        
                        # Usar valores del Excel con sección ARG separada
                        piece_entry = {
                            "name": str(name) if not pd.isna(name) else "Sin nombre",
                            "espanol": str(espanol) if not pd.isna(espanol) and espanol else None,
                            "qty_for_bag": qty_for_bag,
                            "dealer_price": float(dealer_price),
                            "consumer_price": float(consumer_price),
                            "total_in_usa": round(float(total_in_usa), 2),
                            "cost_in_usa_usd": round(float(cost_in_usa_usd), 2),
                            "final_cost_usa": final_cost_value,
                            "ARG": {
                                "weight": weight_grams,
                                "shipping_cost": shipping_cost,
                                "Costo_In_Arg": costo_in_arg,
                                "Ref_Price": ref_price,
                                "Sell_price": sell_price,
                                "Reference_percent": reference_percent
                            }
                        }
                    else:
                        # Calcular usando nuestras fórmulas
                        piece_entry = self.create_piece_entry(
                            code=code,
                            name=str(name) if not pd.isna(name) else "Sin nombre",
                            dealer_price=float(dealer_price),
                            consumer_price=float(consumer_price),
                            espanol=str(espanol) if not pd.isna(espanol) and espanol else None,
                            qty_for_bag=qty_for_bag,
                            weight_grams=weight_grams
                        )
                    
                    database[code] = piece_entry
                    processed += 1
                    
                except Exception as e:
                    print(f"❌ Error procesando fila {index}: {e}")
                    continue
            
            print(f"✅ Procesadas {processed} piezas exitosamente")
            self.pieces_data = database
            return database
            
        except Exception as e:
            print(f"❌ Error cargando desde Excel: {e}")
            return {}
    
    def get_piece(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de una pieza específica.
        
        Args:
            code: Código de la pieza
            
        Returns:
            Dict con información de la pieza o None si no existe
        """
        return self.pieces_data.get(code)
    
    def add_piece(self, code: str, name: str, dealer_price: float, 
                  consumer_price: float, espanol: str = None, 
                  qty_for_bag: int = 1, weight_grams: float = None) -> Dict[str, Any]:
        """
        Agrega una nueva pieza a la base de datos.
        
        Args:
            code: Código único de la pieza
            name: Nombre en inglés
            dealer_price: Precio del distribuidor
            consumer_price: Precio al consumidor
            espanol: Nombre en español
            qty_for_bag: Cantidad por bolsa
            weight_grams: Peso en gramos
            
        Returns:
            Dict con la información de la pieza creada
        """
        piece_entry = self.create_piece_entry(
            code=code,
            name=name,
            dealer_price=dealer_price,
            consumer_price=consumer_price,
            espanol=espanol,
            qty_for_bag=qty_for_bag,
            weight_grams=weight_grams
        )
        
        self.pieces_data[code] = piece_entry
        return piece_entry
    
    def update_piece(self, code: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Actualiza información de una pieza existente.
        
        Args:
            code: Código de la pieza
            **kwargs: Campos a actualizar
            
        Returns:
            Dict con la información actualizada o None si no existe
        """
        if code not in self.pieces_data:
            return None
        
        # Actualizar campos básicos
        basic_fields = ['name', 'espanol', 'qty_for_bag', 'dealer_price', 'consumer_price']
        for field in basic_fields:
            if field in kwargs:
                self.pieces_data[code][field] = kwargs[field]
        
        # Recalcular costos USA si cambió el dealer_price
        if 'dealer_price' in kwargs:
            usa_costs = self.calculate_usa_costs(kwargs['dealer_price'])
            self.pieces_data[code].update(usa_costs)
        
        return self.pieces_data[code]
    
    def save_to_json(self, output_path: str = None) -> str:
        """
        Guarda la base de datos en formato JSON de forma incremental.
        Actualiza solo los productos del Excel y preserva productos agregados manualmente.
        
        Args:
            output_path: Ruta donde guardar (opcional)
            
        Returns:
            Ruta del archivo guardado
        """
        if output_path is None:
            output_dir = Path(__file__).parent.parent.parent / "DataBase" / "Generated"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "mecatech_database.json"
        
        # Cargar datos existentes si el archivo ya existe
        existing_data = {}
        if Path(output_path).exists():
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"📂 Cargando {len(existing_data)} productos existentes")
            except Exception as e:
                print(f"⚠️ Error cargando archivo existente: {e}")
                existing_data = {}
        
        # Combinar datos: actualizar existentes y preservar los que no están en el Excel
        updated_count = 0
        preserved_count = 0
        
        # Actualizar productos del Excel
        for code, piece_data in self.pieces_data.items():
            if code in existing_data:
                existing_data[code] = piece_data  # Actualizar existente
                updated_count += 1
            else:
                existing_data[code] = piece_data  # Agregar nuevo
        
        # Contar productos preservados (que no están en self.pieces_data)
        for code in existing_data:
            if code not in self.pieces_data:
                preserved_count += 1
        
        # Guardar datos combinados
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Base de datos actualizada en: {output_path}")
        print(f"🔄 Productos actualizados/nuevos: {updated_count}")
        print(f"📦 Productos preservados: {preserved_count}")
        print(f"📊 Total de productos: {len(existing_data)}")
        
        return str(output_path)
    
    def load_from_json(self, json_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Carga la base de datos desde un archivo JSON.
        
        Args:
            json_path: Ruta del archivo JSON
            
        Returns:
            Dict con la base de datos cargada
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.pieces_data = json.load(f)
            print(f"📂 Base de datos cargada desde: {json_path}")
            return self.pieces_data
        except Exception as e:
            print(f"❌ Error cargando JSON: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la base de datos.
        
        Returns:
            Dict con estadísticas
        """
        if not self.pieces_data:
            return {"total_pieces": 0}
        
        prices = [piece['dealer_price'] for piece in self.pieces_data.values() if piece['dealer_price'] > 0]
        
        return {
            "total_pieces": len(self.pieces_data),
            "pieces_with_spanish": len([p for p in self.pieces_data.values() if p.get('espanol')]),
            "avg_dealer_price": sum(prices) / len(prices) if prices else 0,
            "min_dealer_price": min(prices) if prices else 0,
            "max_dealer_price": max(prices) if prices else 0,
            "total_value": sum(prices) if prices else 0
        }
    
    def search_pieces(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        Busca piezas por código o nombre.
        
        Args:
            query: Texto a buscar
            
        Returns:
            Dict con piezas que coinciden con la búsqueda
        """
        query = query.lower()
        results = {}
        
        for code, piece in self.pieces_data.items():
            if (query in code.lower() or 
                query in piece['name'].lower() or 
                (piece.get('espanol') and query in piece['espanol'].lower())):
                results[code] = piece
        
        return results
    
    def print_piece_info(self, code: str):
        """Imprime información detallada de una pieza."""
        piece = self.get_piece(code)
        if not piece:
            print(f"❌ Pieza con código '{code}' no encontrada")
            return
        
        print(f"\n{'='*60}")
        print(f"🔧 PIEZA: {code}")
        print(f"{'='*60}")
        print(f"📝 Nombre: {piece['name']}")
        if piece.get('espanol'):
            print(f"🇪🇸 Español: {piece['espanol']}")
        print(f"📦 Cantidad por bolsa: {piece['qty_for_bag']}")
        
        # Leer datos de la sección ARG
        arg_data = piece.get('ARG', {})
        weight = arg_data.get('weight')
        shipping_cost = arg_data.get('shipping_cost', 'N/A')
        costo_in_arg = arg_data.get('Costo_In_Arg', 'N/A')
        ref_price = arg_data.get('Ref_Price', 'N/A')
        sell_price = arg_data.get('Sell_price', 'N/A')
        reference_percent = arg_data.get('Reference_percent', 'N/A')
        
        if weight is not None:
            print(f"⚖️ Peso: {weight} gramos")
        else:
            print(f"⚖️ Peso: No definido")
        print(f"📮 Costo de envío: ${shipping_cost}")
        print(f"🇦🇷 Costo total en ARG: ${costo_in_arg}")
        print(f"💲 Precio referencia: ${ref_price}")
        print(f"💰 Precio de venta: ${sell_price}")
        print(f"📊 Porcentaje referencia: {reference_percent}%")
        print(f"\n💰 PRECIOS:")
        print(f"   Distribuidor: €{piece['dealer_price']}")
        print(f"   Consumidor: €{piece['consumer_price']}")
        print(f"\n🇺🇸 COSTOS USA:")
        print(f"   Total en USA: ${piece['total_in_usa']}")
        print(f"   Costo USD: ${piece['cost_in_usa_usd']}")
        print(f"   Costo final: ${piece['final_cost_usa']}")

def main():
    """Función principal para probar el sistema."""
    print("🏗️ SISTEMA DE BASE DE DATOS MECATECH")
    print("="*50)
    
    # Crear instancia de la base de datos
    db = MecatechDatabase()
    
    # Cargar desde Excel
    database = db.load_from_excel()
    
    if database:
        # Mostrar estadísticas
        stats = db.get_statistics()
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total de piezas: {stats['total_pieces']}")
        print(f"   Con nombre en español: {stats['pieces_with_spanish']}")
        print(f"   Precio promedio: €{stats['avg_dealer_price']:.2f}")
        
        # Guardar en JSON
        db.save_to_json()
        
        # Mostrar ejemplo de una pieza
        if database:
            first_code = list(database.keys())[0]
            print(f"\n💡 EJEMPLO DE PIEZA:")
            db.print_piece_info(first_code)
    
    print(f"\n✅ Proceso completado")

if __name__ == "__main__":
    main()
