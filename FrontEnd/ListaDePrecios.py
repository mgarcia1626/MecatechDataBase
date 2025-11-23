"""
Aplicación Streamlit para visualizar la Base de Datos Mecatech.

Esta aplicación permite explorar y filtrar los datos de piezas 
con información de precios, costos y características.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Configuración de paths
current_dir = Path(__file__).parent
parent_dir = current_dir.parent

def load_database():
    """Carga la base de datos desde el archivo JSON generado."""
    # Intentar diferentes rutas posibles
    possible_paths = [
        parent_dir / "DataBase" / "Generated" / "mecatech_database.json",
        Path("c:/Users/Matias Garcia/OneDrive - UTN.BA/Repo Nuevo/Mecatech_DataBase/MecatechDataBase/DataBase/Generated/mecatech_database.json"),
        current_dir.parent / "DataBase" / "Generated" / "mecatech_database.json"
    ]
    
    json_path = None
    for path in possible_paths:
        if path.exists():
            json_path = path
            break
    
    if json_path is None:
        st.error("❌ No se encontró el archivo de base de datos en ninguna de las ubicaciones:")
        for i, path in enumerate(possible_paths, 1):
            st.error(f"  {i}. {path}")
        st.info(f"� Directorio actual: {current_dir}")
        st.info(f"📂 Directorio padre: {parent_dir}")
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        st.success(f"✅ Base de datos cargada desde: {json_path}")
        return data
    except Exception as e:
        st.error(f"❌ Error cargando la base de datos: {e}")
        return None

def create_dataframe(database_data):
    """Convierte los datos de la base de datos en un DataFrame para visualización."""
    rows = []
    
    for code, piece in database_data.items():
        arg_data = piece.get('ARG', {})
        
        # Lógica para el nombre: priorizar español, usar inglés como fallback
        espanol = piece.get('espanol')
        name_english = piece.get('name', 'N/A')
        
        # Si español existe y no es None/vacío, usarlo; sino usar inglés
        display_name = espanol if (espanol and espanol.strip()) else name_english
        
        row = {
            'Código': code,
            'Nombre': display_name,
            'Español': piece.get('espanol', 'N/A') or 'N/A',
            'Costo en USA': piece.get('final_cost_usa', 0),
            'Costo en ARG': arg_data.get('Costo_In_Arg', 0),
            'Envío': arg_data.get('shipping_cost', 0),
            'Peso': arg_data.get('weight', None),
            'Precio de venta': arg_data.get('Sell_price', 0),
            'Precio de referencia': arg_data.get('Ref_Price', 0),
            'Porcentaje encima de referencia': arg_data.get('Reference_percent', 0),
            'Precio distribuidor': piece.get('dealer_price', 0),
            'Precio consumidor': piece.get('consumer_price', 0)
        }
        rows.append(row)
    
    return pd.DataFrame(rows)

def apply_filters(df, weight_filter, shipping_filter, search_term):
    """Aplica los filtros seleccionados al DataFrame."""
    filtered_df = df.copy()
    
    # Filtro por peso
    if weight_filter[0] > 0 or weight_filter[1] < 1000:
        # Filtrar solo las filas que tienen peso definido
        filtered_df = filtered_df[filtered_df['Peso'].notna()]
        filtered_df = filtered_df[
            (filtered_df['Peso'] >= weight_filter[0]) & 
            (filtered_df['Peso'] <= weight_filter[1])
        ]
    
    # Filtro por envío
    if shipping_filter[0] > 0 or shipping_filter[1] < 100:
        filtered_df = filtered_df[
            (filtered_df['Envío'] >= shipping_filter[0]) & 
            (filtered_df['Envío'] <= shipping_filter[1])
        ]
    
    # Filtro por búsqueda
    if search_term:
        search_term = search_term.lower()
        filtered_df = filtered_df[
            filtered_df['Código'].str.lower().str.contains(search_term, na=False) |
            filtered_df['Nombre'].str.lower().str.contains(search_term, na=False) |
            filtered_df['Español'].str.lower().str.contains(search_term, na=False)
        ]
    
    return filtered_df

def format_currency(value):
    """Formatea valores monetarios."""
    if pd.isna(value) or value == 'N/A':
        return 'N/A'
    return f"${value:,.2f}"

def format_weight(value):
    """Formatea valores de peso."""
    if pd.isna(value):
        return 'No definido'
    return f"{value:,.1f}g"

def format_percentage(value):
    """Formatea valores de porcentaje."""
    if pd.isna(value) or value == 'N/A':
        return 'N/A'
    return f"{value:.1f}%"

def main():
    st.set_page_config(
        page_title="Base de Datos Mecatech",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 Base de Datos Mecatech")
    st.markdown("---")
    
    # Cargar datos
    with st.spinner("Cargando base de datos..."):
        database_data = load_database()
    
    if database_data is None:
        st.stop()
    
    df = create_dataframe(database_data)
    
    # Estadísticas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total de Piezas", len(df))
    
    with col2:
        pieces_with_weight = df['Peso'].notna().sum()
        st.metric("⚖️ Con Peso Definido", pieces_with_weight)
    
    with col3:
        avg_cost = df['Costo en ARG'].mean()
        st.metric("💰 Costo Promedio ARG", f"${avg_cost:,.2f}")
    
    with col4:
        avg_sell_price = df['Precio de venta'].mean()
        st.metric("💵 Precio Venta Promedio", f"${avg_sell_price:,.2f}")
    
    st.markdown("---")
    
    # Filtros y búsqueda
    st.subheader("🔍 Filtros y Búsqueda")
    
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        st.write("**⚖️ Filtro por Peso (gramos)**")
        # Obtener rangos de peso (solo para piezas con peso definido)
        weights_with_data = df[df['Peso'].notna()]['Peso']
        if not weights_with_data.empty:
            min_weight = float(weights_with_data.min())
            max_weight = float(weights_with_data.max())
            weight_filter = st.slider(
                "Rango de peso",
                min_value=0.0,
                max_value=max(1000.0, max_weight),
                value=(0.0, max(1000.0, max_weight)),
                step=5.0,
                key="weight_filter"
            )
        else:
            weight_filter = (0.0, 1000.0)
            st.info("No hay datos de peso disponibles")
    
    with col2:
        st.write("**📮 Filtro por Envío (USD)**")
        min_shipping = float(df['Envío'].min())
        max_shipping = float(df['Envío'].max())
        shipping_filter = st.slider(
            "Rango de costo de envío",
            min_value=0.0,
            max_value=max(100.0, max_shipping),
            value=(0.0, max(100.0, max_shipping)),
            step=0.5,
            key="shipping_filter"
        )
    
    with col3:
        st.write("**🔍 Búsqueda por Código/Nombre**")
        search_term = st.text_input(
            "Buscar pieza",
            placeholder="Ingrese código o nombre...",
            key="search_input"
        )
    
    # Aplicar filtros
    filtered_df = apply_filters(df, weight_filter, shipping_filter, search_term)
    
    st.markdown("---")
    
    # Mostrar resultados
    st.subheader(f"📊 Resultados ({len(filtered_df)} piezas)")
    
    if filtered_df.empty:
        st.warning("⚠️ No se encontraron piezas que coincidan con los filtros aplicados")
    else:
        # Preparar DataFrame para mostrar con formato
        display_df = filtered_df.copy()
        
        # Seleccionar y renombrar columnas para la vista principal
        columns_to_show = {
            'Código': 'Código',
            'Nombre': 'Nombre',
            'Costo en USA': 'Costo USA',
            'Costo en ARG': 'Costo ARG',
            'Envío': 'Envío',
            'Peso': 'Peso',
            'Precio de venta': 'Precio Venta',
            'Precio de referencia': 'Precio Ref.',
            'Porcentaje encima de referencia': '% vs Ref.'
        }
        
        display_df = display_df[list(columns_to_show.keys())].rename(columns=columns_to_show)
        
        # Configurar display options
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "Código": st.column_config.TextColumn("Código", width="small"),
                "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                "Costo USA": st.column_config.NumberColumn(
                    "Costo USA",
                    format="$%.2f",
                    width="small"
                ),
                "Costo ARG": st.column_config.NumberColumn(
                    "Costo ARG", 
                    format="$%.2f",
                    width="small"
                ),
                "Envío": st.column_config.NumberColumn(
                    "Envío",
                    format="$%.2f",
                    width="small"
                ),
                "Peso": st.column_config.NumberColumn(
                    "Peso",
                    format="%.1fg",
                    width="small"
                ),
                "Precio Venta": st.column_config.NumberColumn(
                    "Precio Venta",
                    format="$%.2f",
                    width="small"
                ),
                "Precio Ref.": st.column_config.NumberColumn(
                    "Precio Ref.",
                    format="$%.2f",
                    width="small"
                ),
                "% vs Ref.": st.column_config.NumberColumn(
                    "% vs Ref.",
                    format="%.1f%%",
                    width="small"
                )
            },
            height=400
        )
        
        # Opción para descargar datos filtrados
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar datos filtrados (CSV)",
            data=csv,
            file_name="mecatech_filtered_data.csv",
            mime="text/csv"
        )
    
    # Información adicional
    st.markdown("---")
    st.subheader("ℹ️ Información sobre los Campos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💰 Campos Monetarios:**
        - **Costo USA**: Costo final calculado en USA
        - **Costo ARG**: Costo total en Argentina (incluye envío)
        - **Envío**: Costo de envío calculado por peso
        - **Precio Venta**: Precio sugerido de venta (con margen)
        - **Precio Ref.**: Precio de referencia del mercado
        """)
    
    with col2:
        st.markdown("""
        **📊 Campos Informativos:**
        - **Peso**: Peso de la pieza en gramos
        - **% vs Ref.**: Porcentaje que representa el precio de venta vs el de referencia
        - Un valor > 100% indica precio de venta mayor al de referencia
        - Un valor < 100% indica precio de venta menor al de referencia
        """)

if __name__ == "__main__":
    main()