import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO

st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="✅")

st.title("Gerenciador de Tarefas em PDF")

uploaded_pdf = st.file_uploader("Envie o PDF contendo as tarefas", type=["pdf"])

@st.cache_data(show_spinner=False)
def read_pdf(file_bytes: bytes) -> pd.DataFrame:
    """Lê tabelas de um PDF retornando um DataFrame."""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        df_list = []
        for page in pdf.pages:
            for table in page.extract_tables():
                if table:
                    df_list.append(pd.DataFrame(table[1:], columns=table[0]))
        if df_list:
            return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

if uploaded_pdf is not None:
    pdf_bytes = uploaded_pdf.read()
    df = read_pdf(pdf_bytes)

    if df.empty:
        st.error("Nenhuma tabela foi encontrada no PDF enviado.")
    else:
        st.write("### Todas as Tarefas")
        st.dataframe(df)

        # Converte a coluna Prazo para datas quando possível
        if "Prazo" in df.columns:
            df["Prazo"] = pd.to_datetime(df["Prazo"], errors="coerce")

        with st.sidebar:
            st.header("Filtros")
            responsaveis = df["Responsável"].dropna().unique().tolist() if "Responsável" in df.columns else []
            selected_resp = st.multiselect("Responsável", options=responsaveis, default=responsaveis)
            prazo_ini = st.date_input("Prazo a partir de")
            prazo_fim = st.date_input("Prazo até")

        filtered = df.copy()
        if selected_resp:
            filtered = filtered[filtered["Responsável"].isin(selected_resp)]
        if "Prazo" in filtered.columns:
            if prazo_ini:
                filtered = filtered[filtered["Prazo"] >= pd.to_datetime(prazo_ini)]
            if prazo_fim:
                filtered = filtered[filtered["Prazo"] <= pd.to_datetime(prazo_fim)]

        st.write("### Resultado Filtrado")
        st.dataframe(filtered)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("Baixar CSV", data=csv, file_name="tarefas_filtradas.csv", mime="text/csv")
else:
    st.info("Carregue um PDF para visualizar as tarefas.")
