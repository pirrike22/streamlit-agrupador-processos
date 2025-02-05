import streamlit as st
import pandas as pd

st.title("Agrupador de Processos 📂")

uploaded_file = st.file_uploader("Faça o upload da planilha (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("### Prévia dos dados:")
    st.dataframe(df.head())

    required_columns = ["Número do processo", "Órgão"]
    if all(col in df.columns for col in required_columns):
        df_grouped = df.groupby("Número do processo").apply(lambda x: x).reset_index(drop=True)
        st.write("### Dados Agrupados por Número do Processo:")
        st.dataframe(df_grouped)

        df_count = df.groupby(["Número do processo", "Órgão"]).size().reset_index(name="Quantidade de Repetições")
        st.write("### Contagem de Repetições por Processo e Órgão:")
        st.dataframe(df_count)

        csv = df_count.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar dados agrupados com contagem",
            data=csv,
            file_name="dados_agrupados_contagem.csv",
            mime="text/csv",
        )
    else:
        st.error("A planilha deve conter as colunas 'Número do processo' e 'Órgão'.")
