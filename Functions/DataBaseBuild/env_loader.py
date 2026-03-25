"""
Cargador de variables de entorno para MecatechDataBase.
Lee desde archivo .env (desarrollo local) y desde variables de entorno del sistema (Railway).
"""

import os
from pathlib import Path

# Todas las claves que usa la app
ENV_KEYS = [
    'DEFAULT_PROFIT_MARGIN', 'MIN_PROFIT_MARGIN', 'MAX_PROFIT_MARGIN',
    'DEFAULT_SHIPPING_COST_kg', 'NO_WHEIGHT_Cost', 'Amigos',
    'CURRENCY', 'CURRENCY_SYMBOL', 'DECIMAL_PLACES',
    'USATax', 'shipping_Tax', 'Victor_Earn', 'EuToUsd', 'BrakeExtra'
]

def load_env():
    """Carga variables desde .env (local) y desde os.environ (Railway)."""
    env_vars = {}

    # 1. Intentar cargar desde archivo .env (desarrollo local)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    try:
                        env_vars[key.strip()] = float(value.strip())
                    except ValueError:
                        env_vars[key.strip()] = value.strip()

    # 2. Sobreescribir/complementar con variables del sistema (Railway Variables)
    for key in ENV_KEYS:
        if key in os.environ:
            value = os.environ[key]
            try:
                env_vars[key] = float(value)
            except ValueError:
                env_vars[key] = value

    return env_vars

# Cargar variables globalmente
ENV = load_env()