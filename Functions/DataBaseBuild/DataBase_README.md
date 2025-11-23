# 🏗️ DataBase.py - Sistema de Base de Datos MecatechDataBase

## 🎯 Propósito
Sistema completo para manejar la base de datos de piezas con códigos únicos y características, aplicando cálculos automáticos de costos según las variables de entorno (.env).

---

## 📊 Estructura de Datos Generada

### **Formato JSON de salida:**
```json
{
  "2012-SH4": {
    "name": "COMPLETE SHORT CAR (WITH NEW BRAKE HUB, SILICON SHOCKS, BATTERY HOLDER SET, REAR AND FRONT TITANIUM ANTI-ROLL BAR)",
    "espanol": null,
    "qty_for_bag": 1,
    "dealer_price": 1883.00,
    "consumer_price": 2670.00,
    "total_in_usa": 2429.07,
    "cost_in_usa_usd": 2793.43,
    "final_cost_usa": 3072.80
  }
}
```

---

## 🧮 Fórmulas de Cálculo

### **Variables de entorno utilizadas:**
```env
USATax=0.17          # 17% impuesto USA
shipping_Tax=0.12    # 12% impuesto envío
EuToUsd=1.15        # Factor conversión Euro → USD
Victor_Earn=0.10     # 10% ganancia Victor
```

### **Fórmulas aplicadas automáticamente:**
1. **`total_in_usa`** = `dealer_price × (1 + USATax + shipping_Tax)`
2. **`cost_in_usa_usd`** = `total_in_usa × EuToUsd`  
3. **`final_cost_usa`** = `cost_in_usa_usd × (1 + Victor_Earn)`

---

## 🗺️ Mapa del Sistema

```
📁 DataBaseBuild/
├── 🔧 DataBase.py         ← Clase principal MecatechDatabase
├── ⚙️ env_loader.py       ← Cargador de variables .env
└── 📋 __init__.py         ← Paquete Python

📂 Input:
└── 📊 PriceList.xlsx → Hoja "PriceFinal"

📂 Output:
└── 📄 mecatech_database.json
```

---

## 🚀 Funciones Principales

### 1️⃣ **`MecatechDatabase()`** - Clase Principal
```python
from Functions.DataBaseBuild import MecatechDatabase

db = MecatechDatabase()
```

### 2️⃣ **`load_from_excel(sheet_name="PriceFinal")`** - Cargar Excel
```python
# Carga datos desde Excel y genera estructura JSON
database = db.load_from_excel("PriceFinal")
```
- **📥 Entrada**: Archivo Excel con columnas CODE, name, dealer_price, etc.
- **📤 Salida**: Dict con estructura completa de piezas
- **🔄 Proceso**: Mapea columnas automáticamente, aplica cálculos, valida datos

### 3️⃣ **`calculate_usa_costs(dealer_price)`** - Calcular Costos USA
```python
# Aplica las 3 fórmulas automáticamente
costs = db.calculate_usa_costs(1883.00)
# Resultado: {'total_in_usa': 2429.07, 'cost_in_usa_usd': 2793.43, 'final_cost_usa': 3072.80}
```

### 4️⃣ **`create_piece_entry(code, name, dealer_price, ...)`** - Crear Pieza
```python
# Crear entrada completa para una pieza
piece = db.create_piece_entry(
    code="2012-SH4",
    name="COMPLETE SHORT CAR...",
    dealer_price=1883.00,
    consumer_price=2670.00,
    espanol="AUTO COMPLETO CORTO",
    qty_for_bag=1
)
```

### 5️⃣ **`save_to_json(output_path=None)`** - Guardar JSON
```python
# Guarda la base de datos en formato JSON
json_path = db.save_to_json()  # Guarda en DataBase/Generated/mecatech_database.json
```

### 6️⃣ **`get_piece(code)`** - Obtener Pieza
```python
# Obtener información de pieza específica
piece_info = db.get_piece("2012-SH4")
```

### 7️⃣ **`search_pieces(query)`** - Buscar Piezas
```python
# Buscar por código o nombre
results = db.search_pieces("SHORT CAR")
```

### 8️⃣ **`get_statistics()`** - Estadísticas
```python
# Obtener estadísticas de la base de datos
stats = db.get_statistics()
# {'total_pieces': 150, 'avg_dealer_price': 245.67, ...}
```

---

## 📋 Mapeo de Columnas Excel

El sistema mapea automáticamente estas columnas del Excel:

| Excel Column | Mapea a | Descripción |
|--------------|---------|-------------|
| `CODE`, `code` | `code` | **Código único** (obligatorio) |
| `Name`, `ingles`, `english` | `name` | **Nombre en inglés** |
| `Español`, `espanol`, `spanish` | `espanol` | Nombre en español |
| `Dealer Price`, `dealer_price` | `dealer_price` | **Precio distribuidor** |
| `Consumer Price`, `consumer_price` | `consumer_price` | Precio consumidor |
| `Qty per Bag`, `qty_for_bag` | `qty_for_bag` | Cantidad por bolsa |

---

## 💡 Ejemplos de Uso

### **Ejemplo 1: Cargar desde Excel y guardar JSON**
```python
from Functions.DataBaseBuild import MecatechDatabase

# 1. Crear instancia
db = MecatechDatabase()

# 2. Cargar desde Excel 
database = db.load_from_excel("PriceFinal")

# 3. Guardar en JSON
json_path = db.save_to_json()

print(f"Base de datos guardada: {json_path}")
```

### **Ejemplo 2: Agregar pieza manualmente**
```python
# Agregar nueva pieza con cálculos automáticos
new_piece = db.add_piece(
    code="NEW-001",
    name="NEW PART DESCRIPTION",
    dealer_price=500.00,
    consumer_price=750.00,
    espanol="NUEVA PIEZA",
    qty_for_bag=2
)

print(f"Costo final USA: ${new_piece['final_cost_usa']}")
```

### **Ejemplo 3: Buscar y mostrar información**
```python
# Buscar piezas
results = db.search_pieces("COMPLETE")

# Mostrar información detallada
for code in results:
    db.print_piece_info(code)
```

### **Ejemplo 4: Actualizar precios**
```python
# Actualizar precio (recalcula automáticamente costos USA)
updated = db.update_piece("2012-SH4", dealer_price=2000.00)
print(f"Nuevo costo final: ${updated['final_cost_usa']}")
```

---

## ⚡ Características del Sistema

### ✅ **Automático**
- Mapeo inteligente de columnas Excel
- Cálculos automáticos según fórmulas
- Validación de datos de entrada

### ✅ **Flexible**
- Columnas opcionales (español, qty_for_bag)
- Diferentes nombres de hojas Excel
- Actualización dinámica de precios

### ✅ **Robusto**
- Manejo de errores en datos
- Validación de precios y códigos
- Logging detallado del proceso

### ✅ **Completo**
- CRUD completo (Create, Read, Update, Delete)
- Búsqueda por múltiples campos
- Estadísticas y reportes
- Importación/exportación JSON

---

## 🔧 Variables de Entorno Necesarias

### **En archivo `.env`:**
```env
# Impuestos y costos
USATax=0.17              # Impuesto USA (17%)
shipping_Tax=0.12        # Impuesto envío (12%)
EuToUsd=1.15            # Conversión Euro → USD
Victor_Earn=0.10         # Ganancia Victor (10%)

# Opcional - Configuración empresa
COMPANY_NAME=MECATECH
CURRENCY=USD
```

---

## 🧪 Pruebas y Validación

### **Ejecutar pruebas:**
```bash
# Probar sistema completo
python test_database.py

# Probar solo el módulo DataBase
python Functions/DataBaseBuild/DataBase.py
```

### **Verificar cálculos:**
```python
# Ejemplo: dealer_price = 1883.00
# total_in_usa = 1883.00 × (1 + 0.17 + 0.12) = 2429.07
# cost_in_usa_usd = 2429.07 × 1.15 = 2793.43  
# final_cost_usa = 2793.43 × (1 + 0.10) = 3072.80
```

---

## 📁 Estructura de Archivos Generados

```
DataBase/
├── Inputs/
│   └── PriceList.xlsx        ← Archivo de entrada
└── Generated/
    └── mecatech_database.json ← Base de datos generada
```

---

## 🚨 Solución de Problemas

### **Error: "Hoja 'PriceFinal' no encontrada"**
```python
# El sistema probará automáticamente otras hojas:
# "Sheet1", "Hoja1", "PRECIOS", "DATA", "PIEZAS"
```

### **Error: "Columna CODE no encontrada"**
```
Verificar que el Excel tiene una columna con:
- "CODE", "code", o similar
```

### **Error: "Variables .env no cargadas"**
```
Verificar que existe el archivo .env en la raíz del proyecto
con las variables: USATax, shipping_Tax, EuToUsd, Victor_Earn
```

### **Precios calculados incorrectos**
```python
# Verificar variables en .env
from Functions.DataBaseBuild.env_loader import ENV
print(ENV)  # Debe mostrar USATax=0.17, etc.
```

¡El sistema está completo y listo para procesar tu lista de precios con todos los cálculos automáticos!