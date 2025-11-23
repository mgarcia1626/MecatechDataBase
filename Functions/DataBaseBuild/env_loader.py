"""
Cargador de variables de entorno para MecatechDataBase.
"""

import os
from pathlib import Path

def load_env():
    """Carga las variables del archivo .env"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Convertir a float si es posible
                    try:
                        env_vars[key.strip()] = float(value.strip())
                    except ValueError:
                        env_vars[key.strip()] = value.strip()
    
    return env_vars

# Cargar variables globalmente
ENV = load_env()