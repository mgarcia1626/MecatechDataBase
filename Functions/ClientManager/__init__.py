"""
Módulo de Gestión de Clientes para MecatechDataBase.
"""

from .client_functions import (
    agregar_cliente,
    borrar_cliente,
    buscar_cliente,
    listar_clientes,
    actualizar_cliente,
    verificar_login,
    buscar_clientes_por_texto,
    obtener_estadisticas
)

__all__ = [
    'agregar_cliente',
    'borrar_cliente', 
    'buscar_cliente',
    'listar_clientes',
    'actualizar_cliente',
    'verificar_login',
    'buscar_clientes_por_texto',
    'obtener_estadisticas'
]