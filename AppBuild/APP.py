try:
    # Intenta importación relativa (cuando se ejecuta como módulo)
    from ..Functions.DataImport.excel_utils import read_excel_to_df, extract_column
except ImportError:
    # Si falla, usa importación absoluta agregando el path (ejecución directa)
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from Functions.DataImport.excel_utils import read_excel_to_df, extract_column

def main():
    """Cargar la hoja 'PRECIOS NUEVOS' del archivo de lista de precios y mostrar un preview."""
    path = r"C:\Users\Matias Garcia\OneDrive - UTN.BA\Repo Nuevo\Mecatech_DataBase\MecatechDataBase\DataBase\LISTA DE PRECIOS (1).xlsx"
    data = read_excel_to_df(path, sheet_name="PRECIOS NUEVOS")
    precio_min = extract_column(data, "Precio minimo")
    

if __name__ == '__main__':
    main()