# 🔧 Frontend - Base de Datos Mecatech

## 📝 Descripción
Interfaz web desarrollada con Streamlit para visualizar y explorar la base de datos de piezas Mecatech.

## 🚀 Características

### 📊 Visualización de Datos
- **Tabla completa**: Muestra todos los campos importantes de cada pieza
- **Estadísticas**: Métricas generales de la base de datos
- **Formato amigable**: Valores monetarios, pesos y porcentajes formateados

### 🔍 Filtros Disponibles
- **Peso**: Slider para filtrar por rango de peso en gramos
- **Costo de Envío**: Slider para filtrar por rango de costo de envío en USD
- **Búsqueda**: Campo de texto para buscar por código o nombre

### 📁 Campos Mostrados
| Campo | Descripción |
|-------|-------------|
| Costo USA | `final_cost_usa` - Costo final calculado en USA |
| Costo ARG | `Costo_In_Arg` - Costo total en Argentina |
| Envío | `shipping_cost` - Costo de envío calculado |
| Peso | `weight` - Peso de la pieza en gramos |
| Precio de venta | `Sell_price` - Precio sugerido de venta |
| Precio de referencia | `Ref_Price` - Precio de referencia del mercado |
| % vs Referencia | `Reference_percent` - Porcentaje sobre precio de referencia |

## 🛠️ Instalación y Uso

### Prerrequisitos
```bash
pip install streamlit pandas
```

### Ejecutar la aplicación
```bash
cd FrontEnd
streamlit run streamlit_app.py
```

La aplicación se abrirá automáticamente en tu navegador en: `http://localhost:8501`

## 📋 Funcionalidades

### 🎯 Filtros Interactivos
- **Filtro por Peso**: Permite filtrar piezas por rango de peso (solo piezas con peso definido)
- **Filtro por Envío**: Permite filtrar por rango de costo de envío
- **Búsqueda por Texto**: Busca en código, nombre y nombre en español

### 📈 Estadísticas en Tiempo Real
- Total de piezas en la base de datos
- Cantidad de piezas con peso definido
- Costo promedio en Argentina
- Precio de venta promedio

### 💾 Exportación
- Descarga de datos filtrados en formato CSV
- Mantiene el filtrado aplicado por el usuario

## 🔧 Estructura del Código

### `streamlit_app.py`
```python
# Funciones principales:
- load_database()           # Carga datos desde JSON
- create_dataframe()        # Convierte a DataFrame de pandas
- apply_filters()           # Aplica filtros seleccionados
- format_currency()         # Formatea valores monetarios
- format_weight()           # Formatea valores de peso
- format_percentage()       # Formatea porcentajes
```

## 📊 Interpretación de Datos

### Porcentaje vs Referencia
- **> 100%**: Precio de venta mayor al de referencia (margen alto)
- **< 100%**: Precio de venta menor al de referencia (margen bajo)
- **≈ 100%**: Precio competitivo con el mercado

### Códigos Especiales
- **Códigos 1000+**: Piezas de freno con factor extra aplicado
- **Sin peso**: Piezas que usan costo de envío por defecto

## 🚨 Dependencias
- `streamlit`: Framework web para la interfaz
- `pandas`: Manipulación y análisis de datos
- `json`: Lectura de la base de datos generada
- `pathlib`: Manejo de rutas de archivos

## 📞 Uso
1. La aplicación carga automáticamente `mecatech_database.json`
2. Usa los filtros en la barra lateral para explorar datos
3. La tabla se actualiza en tiempo real según los filtros
4. Descarga los datos filtrados cuando los necesites

## ⚙️ Configuración
La aplicación lee directamente de:
- `../DataBase/Generated/mecatech_database.json`
- Configuración de Streamlit con layout wide
- Formato de página optimizado para visualización de datos

---
*Desarrollado como parte del Sistema de Base de Datos Mecatech*