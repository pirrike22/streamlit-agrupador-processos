%%writefile app.py
import streamlit as st
import pandas as pd

# Configurar o título do app
st.title("Agrupador de Processos 📂")

# Upload da planilha
uploaded_file = st.file_uploader("Faça o upload da planilha (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    # Ler a planilha
    df = pd.read_excel(uploaded_file)

    # Verificar colunas disponíveis
    st.write("### Prévia dos dados:")
    st.dataframe(df.head())

    # Verificar se as colunas necessárias existem
    required_columns = ["Número do processo", "Órgão"]
    if all(col in df.columns for col in required_columns):
        
        # Agrupar os dados por número do processo
        df_grouped = df.groupby("Número do processo").apply(lambda x: x).reset_index(drop=True)
        
        st.write("### Dados Agrupados por Número do Processo:")
        st.dataframe(df_grouped)

        # Contar quantas vezes cada processo aparece
        df_count = df.groupby(["Número do processo", "Órgão"]).size().reset_index(name="Quantidade de Repetições")
        
        st.write("### Contagem de Repetições por Processo e Órgão:")
        st.dataframe(df_count)

        # Baixar os dados agrupados com contagem
        csv = df_count.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar dados agrupados com contagem",
            data=csv,
            file_name="dados_agrupados_contagem.csv",
            mime="text/csv",
        )

    else:
        st.error("A planilha deve conter as colunas 'Número do processo' e 'Órgão'.")
