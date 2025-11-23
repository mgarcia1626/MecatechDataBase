"""Utilities para leer archivos Excel y devolver pandas.DataFrame.

Funciones principales:
- read_excel_to_df(file_path, sheet_name): lee una hoja y devuelve DataFrame.
- extract_column(df, column_identifier): extrae una columna específica de un DataFrame.
- list_sheets(file_path): lista nombres de hojas en el archivo.

Notas:
- Estas utilidades usan `pandas`. Asegúrate de tener instalado `pandas` y un engine como `openpyxl` para archivos xlsx.
"""
from typing import Optional, List, Union, Any
import os
import pandas as pd



class ExcelError(Exception):
    """Excepción genérica para errores de lectura de Excel."""
    pass


def _ensure_pandas_available():
    if pd is None:
        raise ExcelError("pandas no está disponible. Instala pandas (y openpyxl para xlsx) para usar estas funciones.")


def read_excel_to_df(file_path: str, sheet_name: Union[str, int] = 0, engine: Optional[str] = None) -> Any:
    """Lee una hoja de un archivo Excel y devuelve un pandas.DataFrame.

    Entradas:
    - file_path: ruta al archivo (absoluta o relativa).
    - sheet_name: nombre de la hoja (str) o índice (int). Por defecto 0 (primera hoja).
    - engine: opcionalmente especificar engine (ej. 'openpyxl'). Si None, pandas decidirá.

    Salida:
    - pandas.DataFrame con los datos de la hoja solicitada.

    Errores:
    - ExcelError si el archivo no existe o si pandas no está instalado.
    - Cualquier excepción de pandas.read_excel se propaga como está.
    """
    _ensure_pandas_available()

    if not isinstance(file_path, str) or not file_path:
        raise ExcelError("file_path debe ser una cadena no vacía")
    if not os.path.exists(file_path):
        raise ExcelError(f"Archivo no encontrado: {file_path}")

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine=engine)
        return df
    except Exception as e:
        # envolver en ExcelError para una API más consistente
        raise ExcelError(f"Error leyendo '{file_path}' hoja '{sheet_name}': {e}")


def extract_column(df: Any, column_identifier: Union[str, int]) -> Any:
    """Extrae una sola columna de un DataFrame pandas.

    Entradas:
    - df: pandas.DataFrame (salida de read_excel_to_df)
    - column_identifier: nombre de la columna (str) o posición (int, base 0)

    Salida:
    - pandas.Series con los datos de la columna solicitada

    Errores:
    - ExcelError si el DataFrame está vacío, la columna no existe, o el índice está fuera de rango
    """
    _ensure_pandas_available()
    
    if df is None or df.empty:
        raise ExcelError("DataFrame está vacío o es None")
    
    if isinstance(column_identifier, str):
        # Extraer por nombre de columna
        if column_identifier not in df.columns:
            available_cols = df.columns.tolist()
            raise ExcelError(f"Columna '{column_identifier}' no encontrada. Columnas disponibles: {available_cols}")
        return df[column_identifier]
    
    elif isinstance(column_identifier, int):
        # Extraer by posición (índice)
        if column_identifier < 0 or column_identifier >= len(df.columns):
            raise ExcelError(f"Índice {column_identifier} fuera de rango. DataFrame tiene {len(df.columns)} columnas (0-{len(df.columns)-1})")
        return df.iloc[:, column_identifier]
    
    else:
        raise ExcelError("column_identifier debe ser str (nombre) o int (posición)")


def list_sheets(file_path: str) -> List[str]:
    """Devuelve la lista de nombres de hojas en el archivo Excel.

    Entradas:
    - file_path: ruta al archivo.

    Salida:
    - Lista de strings con los nombres de las hojas.
    """
    _ensure_pandas_available()
    if not isinstance(file_path, str) or not file_path:
        raise ExcelError("file_path debe ser una cadena no vacía")
    if not os.path.exists(file_path):
        raise ExcelError(f"Archivo no encontrado: {file_path}")

    try:
        xls = pd.ExcelFile(file_path)
        return xls.sheet_names
    except Exception as e:
        raise ExcelError(f"Error listando hojas en '{file_path}': {e}")

