# 🏪 Sistema de Gestión de Ventas y Pagos

## 📋 Descripción
Sistema completo para gestionar transacciones de ventas y pagos usando CSV como almacenamiento, con validaciones automáticas de clientes y productos desde la base de datos MecatechDataBase.

## 🎯 Funcionalidades Principales

### ➕ **Nueva Transacción**
- **Compra**: Registra venta de producto a cliente
- **Pago**: Registra pago realizado por cliente 
- **Compra-Venta**: Registra intercambio sin afectar balance

### 🔍 **Búsqueda Inteligente**
- Búsqueda por código de pieza
- Búsqueda por nombre (español o inglés)
- Autocompletado de nombres y precios

### 💰 **Gestión de Balances**
- Balance individual por cliente
- Balance general del sistema
- Historial completo de transacciones

### 📊 **Estadísticas en Tiempo Real**
- Total de ventas y pagos
- Clientes y productos únicos
- Balance neto del negocio

## 📁 Estructura de Archivos

```
SalesManager/
├── SalesManager.py      # Clase principal de gestión
├── ventas_app.py       # Interfaz Streamlit
├── __init__.py         # Configuración del módulo
└── README.md           # Documentación
```

## 📄 Estructura del CSV

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Fecha** | Fecha/hora automática | 2025-11-23 15:30:45 |
| **Cliente** | Nombre del cliente | Dante Covino |
| **Codigo_Pieza** | Código del producto | ABC123 |
| **Nombre_Pieza** | Nombre en español/inglés | Pastilla de freno |
| **Precio_Venta** | Precio de la transacción | 150.50 |
| **Tipo_Operacion** | compra/pago/compra-venta | compra |
| **Comentarios** | Notas adicionales | Entrega inmediata |

## 🚀 Cómo Usar

### 1️⃣ **Ejecutar la Aplicación**
```bash
cd Functions/SalesManager
streamlit run ventas_app.py --server.port 8503
```

### 2️⃣ **Acceder a la Interfaz**
- **URL Local**: http://localhost:8503
- **Navegación**: 4 pestañas principales

### 3️⃣ **Registrar Transacción**
1. Seleccionar cliente de la lista
2. Elegir tipo de operación
3. Buscar producto (si aplica)
4. Confirmar precio
5. Agregar comentarios
6. Registrar transacción

## 🔧 Tipos de Operaciones

### 🛒 **Compra**
- **Requiere**: Cliente + Código de pieza
- **Precio**: Se obtiene automáticamente de `Sell_price`
- **Efecto**: Suma al balance del cliente
- **Ejemplo**: Cliente compra pastilla por $150

### 💵 **Pago**
- **Requiere**: Cliente + Monto
- **Código**: No requerido
- **Efecto**: Resta del balance del cliente
- **Ejemplo**: Cliente paga $500 a cuenta

### 🔄 **Compra-Venta**
- **Requiere**: Cliente + Código de pieza
- **Precio**: $0 (no afecta balance)
- **Efecto**: Solo registro, sin impacto económico
- **Ejemplo**: Intercambio de producto usado

## 📊 Interfaz de Usuario

### **Tab 1: Nueva Transacción**
- Formulario de registro
- Búsqueda inteligente de productos
- Validación automática
- Precios sugeridos

### **Tab 2: Ver Transacciones**
- Historial completo filtrable
- Exportación a CSV
- Búsqueda por fecha/cliente/tipo

### **Tab 3: Balances por Cliente**
- Balance individual de cada cliente
- Totales de compras y pagos
- Resumen general del sistema

### **Tab 4: Buscar Productos**
- Catálogo completo de productos
- Búsqueda por múltiples criterios
- Visualización de precios

## ⚙️ Validaciones Automáticas

### ✅ **Clientes**
- Verificación contra `clientes.json`
- Lista desplegable con todos los clientes

### ✅ **Productos**
- Validación contra `mecatech_database.json`
- Autocompletado de nombres
- Precios desde `Sell_price`

### ✅ **Transacciones**
- Campos obligatorios según tipo
- Montos positivos para pagos
- Códigos válidos para compras

## 📈 Cálculos Automáticos

### **Balance por Cliente**
```
Balance = Total Compras - Total Pagos
```

### **Precios Automáticos**
```
Precio = product['ARG']['Sell_price']
```

### **Nombres Inteligentes**
```
Nombre = spanish_name || english_name
```

## 🎯 Características Técnicas

- **🔄 Tiempo Real**: Actualización automática de estadísticas
- **💾 Persistencia**: Almacenamiento en CSV
- **🔍 Búsqueda Rápida**: Índices optimizados
- **📱 Responsive**: Interfaz adaptativa
- **🛡️ Validación**: Controles de integridad

## 📋 Estado del Sistema

### ✅ **Completado**
- [x] Gestión de transacciones CSV
- [x] Validación de clientes y productos
- [x] Búsqueda inteligente
- [x] Cálculo de balances
- [x] Interfaz Streamlit completa
- [x] Exportación de datos

### 🔄 **Mejoras Futuras**
- [ ] Notificaciones de pagos vencidos
- [ ] Reportes gráficos avanzados
- [ ] Integración con sistema de inventario
- [ ] API REST para integraciones
- [ ] Backup automático de datos

## 🚨 Consideraciones Importantes

- **📁 Ubicación CSV**: `DataBase/Generated/ventas_pagos.csv`
- **🔗 Dependencias**: Requiere `clientes.json` y `mecatech_database.json`
- **💾 Backup**: Recomendado respaldar CSV regularmente
- **🔄 Sincronización**: Un solo CSV para todo el sistema

## 🆘 Solución de Problemas

### **Error: Cliente no encontrado**
- Verificar que el cliente existe en `clientes.json`
- Revisar mayúsculas/minúsculas exactas

### **Error: Producto no encontrado**
- Confirmar código en `mecatech_database.json`
- Regenerar base de datos si es necesario

### **Error: No se puede abrir CSV**
- Cerrar Excel si está abierto el archivo
- Verificar permisos de escritura en directorio

---
*Desarrollado como parte del Sistema MecatechDataBase*