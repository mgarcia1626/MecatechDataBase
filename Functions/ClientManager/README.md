# 👥 Gestión de Clientes - MecatechDataBase

## 📋 Descripción
Módulo para gestión de clientes usando archivo JSON como base de datos simple. Proporciona funciones básicas para agregar, buscar, actualizar y eliminar clientes.

## 📁 Estructura de Archivos
- `client_functions.py`: Funciones principales de gestión
- `ejemplo_uso.py`: Ejemplos y menú interactivo
- `__init__.py`: Configuración del módulo

## 🛠️ Funciones Disponibles

### ➕ `agregar_cliente(nombre, password="0000", **kwargs)`
Agrega un nuevo cliente al archivo JSON.

**Parámetros:**
- `nombre`: Nombre único del cliente
- `password`: Contraseña (por defecto "0000")  
- `**kwargs`: Campos adicionales (email, telefono, direccion, etc.)

**Ejemplo:**
```python
agregar_cliente("Juan Pérez", "mi_pass", email="juan@email.com", telefono="123-456-789")
```

### 🗑️ `borrar_cliente(nombre)`
Elimina un cliente del archivo JSON.

**Parámetros:**
- `nombre`: Nombre del cliente a eliminar

**Ejemplo:**
```python
borrar_cliente("Juan Pérez")
```

### 🔍 `buscar_cliente(nombre)`
Busca y retorna los datos de un cliente específico.

**Parámetros:**
- `nombre`: Nombre del cliente a buscar

**Retorna:**
- `Dict`: Datos del cliente o `None` si no existe

**Ejemplo:**
```python
cliente = buscar_cliente("Dante Covino")
if cliente:
    print(f"Password: {cliente['password']}")
```

### 👥 `listar_clientes()`
Retorna lista completa de todos los clientes.

**Retorna:**
- `List[Dict]`: Lista con todos los clientes

**Ejemplo:**
```python
todos = listar_clientes()
for cliente in todos:
    print(cliente['nombre'])
```

### 🔧 `actualizar_cliente(nombre, **kwargs)`
Actualiza datos de un cliente existente.

**Parámetros:**
- `nombre`: Nombre del cliente a actualizar
- `**kwargs`: Campos a modificar

**Ejemplo:**
```python
actualizar_cliente("Juan Pérez", email="nuevo@email.com", telefono="999-888-777")
```

### 🔐 `verificar_login(nombre, password)`
Verifica credenciales de un cliente.

**Parámetros:**
- `nombre`: Nombre del cliente
- `password`: Contraseña a verificar

**Retorna:**
- `bool`: `True` si es correcto, `False` en caso contrario

**Ejemplo:**
```python
if verificar_login("Dante Covino", "0000"):
    print("Login exitoso")
```

### 🔍 `buscar_clientes_por_texto(texto)`
Busca clientes que contengan el texto en su nombre.

**Parámetros:**
- `texto`: Texto a buscar

**Retorna:**
- `List[Dict]`: Clientes que coinciden

**Ejemplo:**
```python
diegos = buscar_clientes_por_texto("Diego")
```

### 📊 `obtener_estadisticas()`
Obtiene estadísticas de la base de datos.

**Retorna:**
- `Dict`: Estadísticas básicas

**Ejemplo:**
```python
stats = obtener_estadisticas()
print(f"Total: {stats['total_clientes']}")
```

## 📄 Estructura del JSON
```json
{
  "clientes": [
    {
      "nombre": "Cliente Ejemplo",
      "password": "0000",
      "email": "cliente@email.com",
      "telefono": "123-456-789",
      "direccion": "Calle Falsa 123"
    }
  ]
}
```

## 🚀 Uso Básico
```python
from Functions.ClientManager import (
    agregar_cliente, 
    buscar_cliente, 
    verificar_login
)

# Agregar cliente
agregar_cliente("Nuevo Cliente", "pass123", email="nuevo@email.com")

# Buscar cliente
cliente = buscar_cliente("Dante Covino")

# Verificar login
if verificar_login("Dante Covino", "0000"):
    print("Acceso autorizado")
```

## 🎯 Menú Interactivo
Ejecuta `ejemplo_uso.py` para acceder al menú interactivo:

```bash
python ejemplo_uso.py
```

## 📊 Estado Actual
- ✅ **38 clientes** precargados
- ✅ **Contraseña uniforme**: "0000" para todos
- ✅ **Funciones CRUD** completas
- ✅ **Búsqueda flexible**
- ✅ **Menú interactivo**

## ⚠️ Consideraciones
- **Archivo único**: Todos los datos en `DataBase/Inputs/clientes.json`
- **Nombres únicos**: No se permiten duplicados
- **Búsqueda insensible**: Case-insensitive por defecto
- **Backup recomendado**: Hacer copias antes de modificaciones masivas

## 🔄 Próximas Mejoras
- [ ] Validación de email
- [ ] Encriptación de contraseñas
- [ ] Logs de actividad
- [ ] Import/Export CSV
- [ ] Interfaz web con Streamlit

---
*Desarrollado como parte del Sistema MecatechDataBase*