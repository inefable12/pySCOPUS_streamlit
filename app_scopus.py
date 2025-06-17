import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pyscopus import Scopus
from io import BytesIO

# Configuración de la página
st.set_page_config(page_title="Buscador SCOPUS", layout="wide")

st.title("🔍 Búsqueda de artículos científicos en SCOPUS usando PyScopus")
st.info("Autor: Dr. Jesus Alvarado-Huayhuaz")

# --- Entrada de usuario ---
api_key = st.text_input("🔑 Ingresa tu clave de API SCOPUS", type="password")
st.markdown("### 🔍 Búsqueda personalizada con operadores lógicos")

term1 = st.text_input("Palabra clave 1", "deferiprona")
logic1 = st.selectbox("Operador entre 1 y 2", ["AND", "OR"])
term2 = st.text_input("Palabra clave 2", "parkinson")
logic2 = st.selectbox("Operador entre 2 y 3", ["AND", "OR"])
term3 = st.text_input("Palabra clave 3", "disease")

# Botón de búsqueda
if st.button("Buscar en SCOPUS"):
    if not api_key:
        st.error("Por favor ingresa tu clave de API SCOPUS.")
    elif not term1.strip():
        st.error("Debes ingresar al menos una palabra clave.")
    else:
        with st.spinner("Buscando artículos en SCOPUS..."):
        # Inicializar conexión Scopus
            scopus = Scopus(api_key)
            # Formatear cadena de búsqueda
            query_parts = []
            if term1:
                query_parts.append(f'"{term1}"')
            if term2:
                query_parts.append(f"{logic1} \"{term2}\"")
            if term3:
                query_parts.append(f"{logic2} \"{term3}\"")
                          
            if query_parts:
                full_query = f"TITLE-ABS-KEY({' '.join(query_parts)})"
                st.code(full_query, language='sql')  # muestra la query generada
            
                st.markdown("### 🔍 Mostrando resultados de dataset cargado")
            
                url_csv = "https://raw.githubusercontent.com/inefable12/deferiprona_parkinson/refs/heads/main/scopus.csv"
                try:
                    df = pd.read_csv(url_csv)
            
                    st.write(f"📄 Dimensiones del dataset: {df.shape}")
                    st.write("🧾 Columnas:", list(df.columns))
                    st.write("📚 Tipos de documento:")
                    st.write(df["Document Type"].value_counts())
            
                    # Gráfico 1: Tipos de documentos
                    st.subheader("📊 Tipos de documentos")
                    fig1, ax1 = plt.subplots()
                    df["Document Type"].value_counts().plot(kind='bar', ax=ax1, color="blue")
                    ax1.set_title("Tipos de documentos")
                    ax1.set_xlabel("Tipo de documento")
                    ax1.set_ylabel("Cantidad")
                    ax1.tick_params(axis='x', rotation=90)
                    st.pyplot(fig1)
            
                    # Gráfico 2: Publicaciones por año
                    st.subheader("📈 Publicaciones por año")
                    fig2, ax2 = plt.subplots()
                    df["Year"].hist(bins=20, range=(2000, 2025), ax=ax2, color="blue")
                    ax2.set_title("Publicaciones por año")
                    ax2.set_xlabel("Año")
                    ax2.set_ylabel("Cantidad")
                    st.pyplot(fig2)
            
                    # Gráfico 3: Citaciones por publicación
                    st.subheader("⭐ Top 10 publicaciones con más citaciones")
                    citation_count_by_publication = df.groupby('Source title')['Cited by'].sum().sort_values(ascending=False)
                    fig3, ax3 = plt.subplots(figsize=(12, 6))
                    citation_count_by_publication.head(10).plot(kind='bar', ax=ax3)
                    ax3.set_title('Top 10 publicaciones con más citaciones')
                    ax3.set_xlabel('Nombre de la publicación')
                    ax3.set_ylabel('Número total de citaciones')
                    ax3.tick_params(axis='x', rotation=90)
                    plt.tight_layout()
                    st.pyplot(fig3)
            
                except Exception as e:
                    st.error(f"❌ Ocurrió un error al cargar el dataset desde GitHub: {e}")               
                
                try:
                    df = scopus.search(full_query, count=200, view='STANDARD')
                    if df.empty:
                        st.warning("No se encontraron resultados.")
                    else:
                        st.success(f"Se encontraron {len(df)} artículos.")
                        
                        # Mostrar tabla
                        st.dataframe(df)
    
                        # Descargar CSV
                        csv_buffer = BytesIO()
                        df.to_csv(csv_buffer, index=False)
                        st.download_button(
                            label="📥 Descargar resultados en CSV",
                            data=csv_buffer.getvalue(),
                            file_name="scopus_results.csv",
                            mime="text/csv"
                        )
    
                        # Gráfica 1: Tipos de documento
                        st.subheader("📊 Tipos de documentos")
                        fig1, ax1 = plt.subplots()
                        df["Document Type"].value_counts().plot(kind='bar', ax=ax1, color="steelblue")
                        ax1.set_title("Tipos de documentos")
                        ax1.set_xlabel("Tipo")
                        ax1.set_ylabel("Cantidad")
                        ax1.tick_params(axis='x', rotation=90)
                        st.pyplot(fig1)
    
                        # Gráfica 2: Publicaciones por año
                        st.subheader("📈 Publicaciones por año (2000–2025)")
                        fig2, ax2 = plt.subplots()
                        df["Year"].hist(bins=20, range=(2000, 2025), ax=ax2, color="skyblue")
                        ax2.set_title("Publicaciones por año")
                        ax2.set_xlabel("Año")
                        ax2.set_ylabel("Cantidad")
                        st.pyplot(fig2)
    
                        # Gráfica 3: Top 10 publicaciones con más citaciones
                        st.subheader("⭐ Top 10 publicaciones con más citaciones")
                        citation_count = df.groupby('Source title')['Cited by'].sum().sort_values(ascending=False)
                        fig3, ax3 = plt.subplots(figsize=(12, 6))
                        citation_count.head(10).plot(kind='bar', ax=ax3, color='green')
                        ax3.set_title('Top 10 publicaciones con más citaciones')
                        ax3.set_xlabel('Nombre de la publicación')
                        ax3.set_ylabel('Número total de citaciones')
                        ax3.tick_params(axis='x', rotation=90)
                        st.pyplot(fig3)
                except Exception as e:
                    st.error(f"Ocurrió un error al consultar la API: {e}")
