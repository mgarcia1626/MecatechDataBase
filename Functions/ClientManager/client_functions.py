"""
Funciones para gestión de clientes usando archivo JSON.

Este módulo proporciona funciones básicas para manejar la base de datos
de clientes almacenada en formato JSON.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

# Configuración de rutas
CURRENT_DIR = Path(__file__).parent
CLIENTS_JSON_PATH = CURRENT_DIR.parent.parent / "DataBase" / "Inputs" / "clientes.json"

def load_clients() -> Dict:
    """
    Carga los datos de clientes desde el archivo JSON.
    
    Returns:
        Dict con la estructura de clientes cargada desde JSON
    """
    try:
        if CLIENTS_JSON_PATH.exists():
            with open(CLIENTS_JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Si no existe, crear estructura vacía
            return {"clientes": []}
    except Exception as e:
        print(f"❌ Error cargando clientes: {e}")
        return {"clientes": []}

def save_clients(clients_data: Dict) -> bool:
    """
    Guarda los datos de clientes al archivo JSON.
    
    Args:
        clients_data: Dict con la estructura de clientes
        
    Returns:
        True si se guardó exitosamente, False en caso contrario
    """
    try:
        # Crear directorio si no existe
        CLIENTS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CLIENTS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(clients_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando clientes: {e}")
        return False

def agregar_cliente(nombre: str, password: str = "0000", **kwargs) -> bool:
    """
    Agrega un nuevo cliente al archivo JSON.
    
    Args:
        nombre: Nombre del cliente (debe ser único)
        password: Contraseña del cliente (por defecto "0000")
        **kwargs: Campos adicionales opcionales (email, telefono, direccion, etc.)
        
    Returns:
        True si se agregó exitosamente, False si ya existe o hay error
    """
    # Cargar datos actuales
    clients_data = load_clients()
    
    # Verificar si el cliente ya existe
    for client in clients_data["clientes"]:
        if client["nombre"].lower() == nombre.lower():
            print(f"❌ El cliente '{nombre}' ya existe")
            return False
    
    # Crear nuevo cliente
    new_client = {
        "nombre": nombre,
        "password": password
    }
    
    # Agregar campos adicionales si se proporcionan
    for key, value in kwargs.items():
        new_client[key] = value
    
    # Agregar a la lista
    clients_data["clientes"].append(new_client)
    
    # Guardar
    if save_clients(clients_data):
        print(f"✅ Cliente '{nombre}' agregado exitosamente")
        return True
    else:
        print(f"❌ Error agregando cliente '{nombre}'")
        return False

def borrar_cliente(nombre: str) -> bool:
    """
    Borra un cliente del archivo JSON.
    
    Args:
        nombre: Nombre del cliente a borrar
        
    Returns:
        True si se borró exitosamente, False si no existe o hay error
    """
    # Cargar datos actuales
    clients_data = load_clients()
    
    # Buscar y remover cliente
    original_count = len(clients_data["clientes"])
    clients_data["clientes"] = [
        client for client in clients_data["clientes"] 
        if client["nombre"].lower() != nombre.lower()
    ]
    
    # Verificar si se removió algún cliente
    if len(clients_data["clientes"]) == original_count:
        print(f"❌ Cliente '{nombre}' no encontrado")
        return False
    
    # Guardar cambios
    if save_clients(clients_data):
        print(f"✅ Cliente '{nombre}' borrado exitosamente")
        return True
    else:
        print(f"❌ Error borrando cliente '{nombre}'")
        return False

def buscar_cliente(nombre: str) -> Optional[Dict]:
    """
    Busca los datos de un cliente específico.
    
    Args:
        nombre: Nombre del cliente a buscar
        
    Returns:
        Dict con los datos del cliente o None si no se encuentra
    """
    # Cargar datos actuales
    clients_data = load_clients()
    
    # Buscar cliente (búsqueda case-insensitive)
    for client in clients_data["clientes"]:
        if client["nombre"].lower() == nombre.lower():
            return client
    
    print(f"❌ Cliente '{nombre}' no encontrado")
    return None

def listar_clientes() -> List[Dict]:
    """
    Lista todos los clientes.
    
    Returns:
        Lista de diccionarios con información de todos los clientes
    """
    clients_data = load_clients()
    return clients_data["clientes"]

def buscar_clientes_por_texto(texto: str) -> List[Dict]:
    """
    Busca clientes que contengan el texto en su nombre.
    
    Args:
        texto: Texto a buscar en los nombres
        
    Returns:
        Lista de clientes que coinciden con la búsqueda
    """
    clients_data = load_clients()
    texto_lower = texto.lower()
    
    matching_clients = []
    for client in clients_data["clientes"]:
        if texto_lower in client["nombre"].lower():
            matching_clients.append(client)
    
    return matching_clients

def actualizar_cliente(nombre: str, **kwargs) -> bool:
    """
    Actualiza los datos de un cliente existente.
    
    Args:
        nombre: Nombre del cliente a actualizar
        **kwargs: Campos a actualizar
        
    Returns:
        True si se actualizó exitosamente, False si no existe o hay error
    """
    # Cargar datos actuales
    clients_data = load_clients()
    
    # Buscar y actualizar cliente
    client_found = False
    for client in clients_data["clientes"]:
        if client["nombre"].lower() == nombre.lower():
            # Actualizar campos proporcionados
            for key, value in kwargs.items():
                client[key] = value
            client_found = True
            break
    
    if not client_found:
        print(f"❌ Cliente '{nombre}' no encontrado")
        return False
    
    # Guardar cambios
    if save_clients(clients_data):
        print(f"✅ Cliente '{nombre}' actualizado exitosamente")
        return True
    else:
        print(f"❌ Error actualizando cliente '{nombre}'")
        return False

def verificar_login(nombre: str, password: str) -> bool:
    """
    Verifica las credenciales de un cliente.
    
    Args:
        nombre: Nombre del cliente
        password: Contraseña del cliente
        
    Returns:
        True si las credenciales son correctas, False en caso contrario
    """
    client = buscar_cliente(nombre)
    if client and client.get("password") == password:
        print(f"✅ Login exitoso para '{nombre}'")
        return True
    else:
        print(f"❌ Credenciales incorrectas para '{nombre}'")
        return False

def obtener_estadisticas() -> Dict:
    """
    Obtiene estadísticas de la base de datos de clientes.
    
    Returns:
        Dict con estadísticas básicas
    """
    clients_data = load_clients()
    total_clients = len(clients_data["clientes"])
    
    # Contar clientes con campos adicionales
    clients_with_email = len([c for c in clients_data["clientes"] if c.get("email")])
    clients_with_phone = len([c for c in clients_data["clientes"] if c.get("telefono")])
    clients_with_address = len([c for c in clients_data["clientes"] if c.get("direccion")])
    
    return {
        "total_clientes": total_clients,
        "clientes_con_email": clients_with_email,
        "clientes_con_telefono": clients_with_phone,
        "clientes_con_direccion": clients_with_address
    }

def main():
    """Función de prueba para demostrar las funcionalidades."""
    print("🏗️ SISTEMA DE GESTIÓN DE CLIENTES - JSON")
    print("=" * 50)
    
    # Mostrar estadísticas iniciales
    print("\n📊 ESTADÍSTICAS INICIALES:")
    stats = obtener_estadisticas()
    print(f"   Total de clientes: {stats['total_clientes']}")
    
    # Mostrar algunos clientes
    print("\n👥 PRIMEROS 5 CLIENTES:")
    clients = listar_clientes()[:5]
    for i, client in enumerate(clients, 1):
        print(f"   {i}. {client['nombre']}")
    
    # Prueba de búsqueda
    print("\n🔍 PRUEBA DE BÚSQUEDA:")
    client_data = buscar_cliente("Dante Covino")
    if client_data:
        print(f"   Encontrado: {client_data['nombre']}")
        print(f"   Password: {client_data['password']}")
    
    # Prueba de login
    print("\n🔐 PRUEBA DE LOGIN:")
    verificar_login("Dante Covino", "0000")
    verificar_login("Dante Covino", "wrong_password")
    
    # Prueba de búsqueda por texto
    print("\n🔍 BÚSQUEDA POR TEXTO 'Diego':")
    diegos = buscar_clientes_por_texto("Diego")
    for diego in diegos:
        print(f"   - {diego['nombre']}")
    
    # Prueba de agregar cliente (comentado para no modificar datos reales)
    # print("\n➕ AGREGANDO CLIENTE DE PRUEBA:")
    # agregar_cliente("Cliente Prueba", "1234", email="prueba@test.com")
    
    print("\n✅ Todas las funciones están operativas")

if __name__ == "__main__":
    main()