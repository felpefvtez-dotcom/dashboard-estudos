import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Performance de Estudos", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS PREMIUM (PINK & DARK)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FF2E63 !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #AEB2B7 !important; }
    [data-testid="stMetricValue"] { color: #08D9D6 !important; }
    
    /* Botão de Registro */
    div.stLinkButton > a {
        background-color: #FF2E63 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        text-decoration: none !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LINKS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIz3YX4UyzZfg6d03AiQ-EyHifW1ezl8gh-3jJUKZjnBLhi0bYEYTVjtu-ag0QnW0QyzCkhgsKs467/pub?gid=1785346654&single=true&output=csv"
URL_FORM = "https://forms.gle/zMyh8ZWvZ4mYSxmu7"

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [c.strip() for c in df.columns]
        
        # --- LÓGICA DE UNIFICAÇÃO DE TEMAS (Resolve erro de múltiplas seções) ---
        cols_tema = [c for c in df.columns if 'Tema' in c]
        if cols_tema:
            df['Tema_Unificado'] = df[cols_tema].bfill(axis=1).iloc[:, 0]
            df = df.drop(columns=cols_tema).rename(columns={'Tema_Unificado': 'Tema'})
        
        # Limpeza e Conversão
        df = df.dropna(subset=['Tipo de Atividade', 'Questões Resolvidas'])
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        df['Erros'] = df['Questões Resolvidas'] - df['Acertos']
        df['Taxa de Erro'] = (df['Erros'] / df['Questões Resolvidas']).fillna(0)
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

# 4. HEADER
col_tit, col_btn = st.columns([3, 1])
with col_tit:
    st.title("Performance de Estudos")
with col_btn:
    st.link_button("Registrar Novo Estudo", URL_FORM, use_container_width=True)

if df_raw.empty:
    st.warning("Aguardando dados... Preencha o formulário e aguarde a atualização.")
else:
    # --- FILTROS ---
    st.sidebar.markdown("### Filtros")
    lista_atv = ["Todas"] + sorted([str(x) for x in df_raw['Tipo de Atividade'].unique()])
    filtro_atv = st.sidebar.selectbox("Tipo de Atividade", lista_atv)
    df = df_raw if filtro_atv == "Todas" else df_raw[df_raw['Tipo de Atividade'] == filtro_atv]

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    q, a = df['Questões Resolvidas'].sum(), df['Acertos'].sum()
    m1.metric("Questões", int(q))
    m2.metric("Acertos", int(a))
    m3.metric("Aproveitamento", f"{(a/q*100):.1f}%" if q > 0 else "0%")
    m4.metric("Tempo Total", f"{df['Tempo de Estudo em Minutos'].sum()/60:.1f}h")

    st.markdown("---")

    # --- LINHA 1 DE GRÁFICOS ---
    g1, g2 = st.columns(2)
    cores_base = ['#FF2E63', '#08D9D6', '#6A2C70', '#B83B5E', '#F08A5D']

    with g1:
        st.subheader("Distribuição por Área")
        fig1 = px.pie(df, values='Questões Resolvidas', names='Grande Área', hole=0.5, color_discrete_sequence=cores_base)
        fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        st.subheader("Relação Acertos x Erros")
        resumo = df.groupby('Grande Área')[['Acertos', 'Erros']].sum().reset_index()
        fig2 = px.bar(resumo, x='Grande Área', y=['Acertos', 'Erros'], barmode='group', 
                      color_discrete_map={'Acertos': '#08D9D6', 'Erros': '#FF2E63'})
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    # --- LINHA 2 DE GRÁFICOS ---
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("Top 5 Temas com Mais Erros")
        temas = df.groupby('Tema')['Taxa de Erro'].mean().sort_values(ascending=False).head(5).reset_index()
        fig3 = px.bar(temas, x='Taxa de Erro', y='Tema', orientation='h', color_discrete_sequence=['#FF2E63'])
        fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", xaxis_tickformat='.0%')
        st.plotly_chart(fig3, use_container_width=True)

    with g4:
        st.subheader("Evolução Temporal")
        evol = df.groupby('Data')[['Questões Resolvidas', 'Acertos']].sum().reset_index()
        fig4 = px.line(evol, x='Data', y=['Questões Resolvidas', 'Acertos'], markers=True, 
                       color_discrete_sequence=['#FF2E63', '#08D9D6'])
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig4, use_container_width=True)
