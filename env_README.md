# 📋 Sistema de Variables de Entorno (.env)

## 🎯 Propósito
Sistema centralizado para manejar variables de negocio que pueden cambiar durante la operación del sistema MecatechDataBase.

---

## 📁 Archivos del Sistema

```
MecatechDataBase/
├── .env              ← Variables de configuración
├── env_config.py     ← Módulo para cargar las variables  
└── example_env_usage.py ← Ejemplo de uso
```

---

## 🔧 Variables Disponibles

### 💰 **MÁRGENES DE GANANCIA**
```env
DEFAULT_PROFIT_MARGIN=30.0     # Margen por defecto (%)
MIN_PROFIT_MARGIN=10.0         # Margen mínimo permitido (%)  
MAX_PROFIT_MARGIN=100.0        # Margen máximo permitido (%)
```

### 🎯 **DESCUENTOS**
```env
MAX_DISCOUNT_PERCENTAGE=25.0   # Descuento máximo (%)
BULK_DISCOUNT_THRESHOLD=10     # Cantidad para descuento mayorista
BULK_DISCOUNT_PERCENTAGE=5.0   # Descuento mayorista (%)
```

### 📊 **IMPUESTOS**
```env
TAX_RATE=21.0                  # IVA o impuesto (%)
TAX_INCLUDED=true              # Si los precios incluyen impuestos
```

### 📦 **CONTROL DE STOCK**
```env
LOW_STOCK_THRESHOLD=10         # Límite para alertas de stock bajo
CRITICAL_STOCK_THRESHOLD=5     # Límite crítico
MAX_STOCK_CAPACITY=1000        # Capacidad máxima del almacén
ENABLE_STOCK_ALERTS=true       # Habilitar alertas automáticas
```

### 🏢 **INFORMACIÓN DE EMPRESA**
```env
COMPANY_NAME=MECATECH          # Nombre de la empresa
CURRENCY=ARS                   # Moneda (ARS, USD, etc.)
CURRENCY_SYMBOL=$              # Símbolo de moneda
DECIMAL_PLACES=2               # Decimales para mostrar precios
```

---

## 🚀 Cómo Usar

### 1️⃣ **Importar el módulo**
```python
from env_config import (
    DEFAULT_PROFIT_MARGIN,
    MAX_DISCOUNT_PERCENTAGE,
    TAX_RATE,
    LOW_STOCK_THRESHOLD,
    format_currency,
    get_price_with_margin
)
```

### 2️⃣ **Usar las variables**
```python
# Calcular precio con margen
costo = 100.0
precio_venta = get_price_with_margin(costo)  # Usa DEFAULT_PROFIT_MARGIN

# Verificar stock
if is_low_stock(stock_actual):
    print("⚠️ Stock bajo!")

# Formatear precios
precio_formateado = format_currency(precio_venta)
print(f"Precio: {precio_formateado}")
```

### 3️⃣ **Cambiar variables durante ejecución**
```python
# Modificar el archivo .env directamente o:
import env_config
env_config.DEFAULT_PROFIT_MARGIN = 35.0
env_config.MAX_DISCOUNT_PERCENTAGE = 20.0
```

---

## 🔄 Funciones Incluidas

| Función | Propósito | Ejemplo |
|---------|-----------|---------|
| `get_price_with_margin(cost, margin)` | Precio + margen | `get_price_with_margin(100.0)` → `130.0` |
| `get_price_with_tax(price, include_tax)` | Precio + impuestos | `get_price_with_tax(100.0)` → `121.0` |
| `apply_discount(price, discount, max_discount)` | Aplicar descuento | `apply_discount(100.0, 10.0)` → `90.0` |
| `format_currency(amount)` | Formatear como moneda | `format_currency(100.5)` → `"$ 100.50"` |
| `is_low_stock(quantity)` | ¿Stock bajo? | `is_low_stock(8)` → `True` |
| `is_critical_stock(quantity)` | ¿Stock crítico? | `is_critical_stock(3)` → `True` |

---

## 💡 Ejemplos Prácticos

### **Ejemplo 1: Calcular precio de venta completo**
```python
from env_config import *

costo_producto = 85.0

# 1. Aplicar margen
precio_con_margen = get_price_with_margin(costo_producto)  # 85 → 110.50

# 2. Agregar impuestos
precio_final = get_price_with_tax(precio_con_margen)       # 110.50 → 133.71

# 3. Formatear para mostrar
precio_mostrar = format_currency(precio_final)             # "$ 133.71"

print(f"Costo: {format_currency(costo_producto)}")
print(f"Precio final: {precio_mostrar}")
```

### **Ejemplo 2: Control de stock con alertas**
```python
from env_config import *

def revisar_stock(producto, cantidad):
    if is_critical_stock(cantidad):
        return f"🔴 {producto}: STOCK CRÍTICO ({cantidad} unidades)"
    elif is_low_stock(cantidad):
        return f"🟡 {producto}: Stock bajo ({cantidad} unidades)"
    else:
        return f"🟢 {producto}: Stock normal ({cantidad} unidades)"

productos = [
    ("Producto A", 3),
    ("Producto B", 8),  
    ("Producto C", 25)
]

for producto, stock in productos:
    print(revisar_stock(producto, stock))
```

### **Ejemplo 3: Sistema de descuentos**
```python
from env_config import *

def calcular_precio_cliente(precio_base, cantidad, es_mayorista=False):
    """Calcular precio final según tipo de cliente y cantidad."""
    
    precio = precio_base
    
    # Descuento por cantidad
    if cantidad >= BULK_DISCOUNT_THRESHOLD:
        precio = apply_discount(precio, BULK_DISCOUNT_PERCENTAGE)
        print(f"Descuento mayorista aplicado: {BULK_DISCOUNT_PERCENTAGE}%")
    
    # Descuento adicional para mayoristas
    if es_mayorista:
        descuento_extra = 5.0
        precio = apply_discount(precio, descuento_extra)
        print(f"Descuento mayorista adicional: {descuento_extra}%")
    
    return precio

# Ejemplo de uso
precio_unitario = 100.0
cantidad_compra = 15

precio_final = calcular_precio_cliente(precio_unitario, cantidad_compra, es_mayorista=True)
print(f"Precio final: {format_currency(precio_final * cantidad_compra)}")
```

---

## 🎛️ Modificar Variables

### **Opción 1: Editar archivo .env**
```env
# Cambiar margen por defecto de 30% a 35%
DEFAULT_PROFIT_MARGIN=35.0

# Cambiar límite de stock bajo de 10 a 15
LOW_STOCK_THRESHOLD=15
```

### **Opción 2: Modificar durante ejecución**
```python
import env_config

# Cambiar para temporada alta
env_config.LOW_STOCK_THRESHOLD = 20
env_config.CRITICAL_STOCK_THRESHOLD = 10

# Cambiar márgenes para promoción
env_config.DEFAULT_PROFIT_MARGIN = 25.0
env_config.MAX_DISCOUNT_PERCENTAGE = 35.0
```

---

## ✅ Ventajas del Sistema

✅ **Centralizado**: Todas las variables de negocio en un lugar  
✅ **Fácil modificación**: Cambiar valores sin tocar código  
✅ **Tipado automático**: Convierte strings a int/float/bool automáticamente  
✅ **Funciones incluidas**: Cálculos comunes ya programados  
✅ **Validación**: Las funciones validan rangos y límites  
✅ **Formato consistente**: Moneda y decimales configurables  
✅ **Reutilizable**: Importar solo lo que necesites  

---

## 🔧 Para Desarrolladores

### **Agregar nueva variable:**
1. Agregar al archivo `.env`:
   ```env
   NEW_VARIABLE=valor_por_defecto
   ```

2. Agregar al `env_config.py`:
   ```python
   NEW_VARIABLE = get_env_value('NEW_VARIABLE', valor_defecto, tipo)
   ```

### **Agregar nueva función de cálculo:**
```python
def nueva_funcion_calculo(parametros):
    """Descripción de la función."""
    # Usar variables globales como DEFAULT_PROFIT_MARGIN
    # Retornar resultado calculado
    pass
```

¡Ahora tienes un sistema completo y flexible para manejar todas las variables de negocio!