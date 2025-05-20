import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO

st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="✅", layout="wide")

st.title("Gerenciador de Tarefas em PDF")

# Inicializa o armazenamento de tarefas persistente em sessao
if "tarefas" not in st.session_state:
    st.session_state["tarefas"] = pd.DataFrame()

uploaded_pdf = st.file_uploader(
    "Anexe um PDF com as tarefas", type=["pdf"], accept_multiple_files=False
)

@st.cache_data(show_spinner=False)
def pdf_to_df(file_bytes: bytes) -> pd.DataFrame:
    """Extrai tabelas de um PDF retornando um DataFrame."""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        tables = []
        for page in pdf.pages:
            for table in page.extract_tables():
                if table:
                    tables.append(pd.DataFrame(table[1:], columns=table[0]))
        return pd.concat(tables, ignore_index=True) if tables else pd.DataFrame()

if uploaded_pdf is not None:
    pdf_bytes = uploaded_pdf.read()
    novas_tarefas = pdf_to_df(pdf_bytes)
    if novas_tarefas.empty:
        st.warning("Nenhuma tabela foi encontrada no PDF.")
    else:
        st.session_state["tarefas"] = pd.concat(
            [st.session_state["tarefas"], novas_tarefas], ignore_index=True
        )
        st.success("Tarefas adicionadas!")

# Dados atuais
df = st.session_state["tarefas"]

if df.empty:
    st.info("Nenhuma tarefa carregada. Envie um PDF para começar.")
    st.stop()

# Converte a coluna Prazo para datetime quando existir
if "Prazo" in df.columns:
    df["Prazo"] = pd.to_datetime(df["Prazo"], errors="coerce")

with st.sidebar:
    st.header("Filtros")
    responsaveis = df["Responsável"].dropna().unique().tolist() if "Responsável" in df.columns else []
    selected_resp = st.multiselect("Responsável", options=responsaveis, default=responsaveis)
    data_ini = st.date_input("Prazo a partir de", value=None)
    data_fim = st.date_input("Prazo até", value=None)
    if st.button("Limpar tarefas"):
        st.session_state["tarefas"] = pd.DataFrame()
        st.experimental_rerun()

filtro = df.copy()
if selected_resp:
    filtro = filtro[filtro["Responsável"].isin(selected_resp)]
if "Prazo" in filtro.columns:
    if data_ini:
        filtro = filtro[filtro["Prazo"] >= pd.to_datetime(data_ini)]
    if data_fim:
        filtro = filtro[filtro["Prazo"] <= pd.to_datetime(data_fim)]

st.subheader("Tarefas Filtradas")
st.dataframe(filtro, use_container_width=True)

csv = filtro.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Baixar CSV",
    data=csv,
    file_name="tarefas_filtradas.csv",
    mime="text/csv",
)
