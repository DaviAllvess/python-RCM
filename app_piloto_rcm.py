
import streamlit as st
import json
import pandas as pd
from pathlib import Path

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================

st.set_page_config(
    page_title="RCM Presidente Figueiredo - Piloto",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================

@st.cache_data
def load_data():
    json_path = Path(__file__).parent / "matriz_curricular_rcm_2026.json"

    if not json_path.exists():
        raise FileNotFoundError(
            "O arquivo matriz_curricular_rcm_2026.json não foi encontrado."
        )

    with open(json_path, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


try:
    data = load_data()
    df = pd.DataFrame(data)

    if df.empty:
        st.error("O arquivo JSON não possui habilidades cadastradas.")
        st.stop()

except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()


# ==========================================
# VERIFICAÇÃO DAS COLUNAS
# ==========================================

colunas_obrigatorias = [
    "id_habilidade",
    "componente_curricular",
    "etapa_ano",
    "bimestre",
    "descricao_habilidade",
    "codigo_bncc_co",
    "eixo_computacao",
    "dimensao_rcm",
    "inteligencias_multiplas",
    "praxis_territorio"
]

colunas_faltantes = [
    coluna for coluna in colunas_obrigatorias
    if coluna not in df.columns
]

if colunas_faltantes:
    st.error(
        "O arquivo JSON não possui estas colunas: "
        + ", ".join(colunas_faltantes)
    )
    st.stop()


# ==========================================
# TÍTULO
# ==========================================

st.title("📚 RCM 2026 - Consulta & Planejamento Curricular")

st.caption(
    "Piloto de consulta do Referencial Curricular Municipal "
    "de Presidente Figueiredo"
)

st.divider()


# ==========================================
# FILTROS DE BUSCA
# ==========================================

st.sidebar.header("🔍 Filtros de Busca")


def opcoes_coluna(coluna, todos):
    valores = df[coluna].dropna().astype(str).unique().tolist()
    return [todos] + sorted(valores)


componentes = opcoes_coluna("componente_curricular", "Todos")
comp_sel = st.sidebar.selectbox(
    "Componente Curricular", componentes
)

anos = opcoes_coluna("etapa_ano", "Todos")
ano_sel = st.sidebar.selectbox(
    "Etapa / Ano", anos
)

bimestres = opcoes_coluna("bimestre", "Todos")
bim_sel = st.sidebar.selectbox(
    "Bimestre", bimestres
)

dimensoes = opcoes_coluna("dimensao_rcm", "Todas")
dim_sel = st.sidebar.selectbox(
    "Dimensão do RCM", dimensoes
)


# ==========================================
# FILTRAGEM
# ==========================================

df_filtered = df.copy()

if comp_sel != "Todos":
    df_filtered = df_filtered[
        df_filtered["componente_curricular"] == comp_sel
    ]

if ano_sel != "Todos":
    df_filtered = df_filtered[
        df_filtered["etapa_ano"] == ano_sel
    ]

if bim_sel != "Todos":
    df_filtered = df_filtered[
        df_filtered["bimestre"] == bim_sel
    ]

if dim_sel != "Todas":
    df_filtered = df_filtered[
        df_filtered["dimensao_rcm"] == dim_sel
    ]


# ==========================================
# RESULTADOS
# ==========================================

st.subheader(
    f"📋 Habilidades Encontradas ({len(df_filtered)})"
)

if df_filtered.empty:
    st.warning(
        "Nenhuma habilidade encontrada com os filtros selecionados."
    )


# ==========================================
# EXIBIÇÃO DAS HABILIDADES
# ==========================================

for idx, row in df_filtered.iterrows():

    codigo = row.get("id_habilidade", "Sem código")
    componente = row.get("componente_curricular", "Não informado")
    etapa = row.get("etapa_ano", "Não informado")
    bimestre = row.get("bimestre", "Não informado")

    with st.expander(
        f"📌 [{codigo}] {componente} - {etapa} ({bimestre})",
        expanded=False
    ):

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"**BNCC Nacional:** `{codigo}`"
            )

            st.markdown(
                f"**BNCC Computação:** "
                f"`{row.get('codigo_bncc_co', 'N/A')}`"
            )

            st.markdown(
                f"**Dimensão RCM:** "
                f"{row.get('dimensao_rcm', 'Não informada')}"
            )

        with col2:
            st.markdown(
                f"**Inteligências Múltiplas:** "
                f"{row.get('inteligencias_multiplas', 'Não informado')}"
            )

            st.markdown(
                f"**Eixo Computação:** "
                f"{row.get('eixo_computacao', 'Não informado')}"
            )

        st.markdown(
            f"**Descrição da Habilidade:**\n\n"
            f"{row.get('descricao_habilidade', 'Não informada')}"
        )

        st.info(
            "🌿 **Práxis Territorial (Presidente Figueiredo):**\n\n"
            f"{row.get('praxis_territorio', 'Não informada')}"
        )

        if st.button(
            "📝 Criar Plano com esta Habilidade",
            key=f"btn_{idx}"
        ):

            st.session_state["selected_habilidade"] = row.to_dict()

            st.success(
                "Habilidade selecionada! "
                "Preencha o gerador de plano de aula abaixo."
            )


# ==========================================
# GERADOR DE PLANO DE AULA
# ==========================================

st.divider()

st.header("✏️ Gerador de Plano de Aula")

if "selected_habilidade" in st.session_state:

    hab = st.session_state["selected_habilidade"]

    codigo = hab.get("id_habilidade", "Sem código")

    st.success(
        f"Habilidade selecionada: {codigo} - "
        f"{hab.get('componente_curricular', '')} "
        f"({hab.get('etapa_ano', '')})"
    )

    with st.form("plano_form"):

        turma = st.text_input(
            "Turma",
            value="6º Ano A"
        )

        data_aula = st.date_input(
            "Data da Aula"
        )

        metodologia = st.text_area(
            "Metodologia & Atividades",
            value=(
                "Aula baseada na práxis territorial: "
                f"{hab.get('praxis_territorio', '')}"
            )
        )

        recursos = st.text_input(
            "Recursos Didáticos",
            value="Quadro, cartazes, material impresso RCM"
        )

        submitted = st.form_submit_button(
            "💾 Salvar & Exportar Plano"
        )

    if submitted:

        plano_txt = f"""=== PLANO DE AULA (RCM 2026) ===

Turma: {turma}
Data: {data_aula}

Componente Curricular: {hab.get('componente_curricular', '')}
Etapa/Ano: {hab.get('etapa_ano', '')}
Bimestre: {hab.get('bimestre', '')}

BNCC Nacional: {codigo}
BNCC Computação: {hab.get('codigo_bncc_co', 'N/A')}

Dimensão RCM: {hab.get('dimensao_rcm', '')}
Inteligências Múltiplas: {hab.get('inteligencias_multiplas', '')}
Eixo Computação: {hab.get('eixo_computacao', '')}

DESCRIÇÃO DA HABILIDADE:
{hab.get('descricao_habilidade', '')}

PRÁXIS TERRITORIAL:
{hab.get('praxis_territorio', '')}

METODOLOGIA E ATIVIDADES:
{metodologia}

RECURSOS DIDÁTICOS:
{recursos}

=== FIM DO PLANO ===
"""

        st.text_area(
            "Plano Gerado (Pronto para copiar)",
            value=plano_txt,
            height=350
        )

        st.download_button(
            "📥 Baixar Plano de Aula (.txt)",
            data=plano_txt,
            file_name=f"plano_{codigo}.txt",
            mime="text/plain"
        )

else:

    st.info(
        "Selecione uma habilidade acima para preencher "
        "o gerador de plano de aula."
    )
