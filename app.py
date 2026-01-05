import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Performance de Estudos", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS PARA APARÊNCIA PREMIUM (PINK & DARK)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FF2E63 !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    .stMetric label { color: #AEB2B7 !important; }
    .stMetric div { color: #08D9D6 !important; }
    
    /* Botão de Registro */
    div.stLinkButton > a {
        background-color: #FF2E63 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        transition: 0.3s;
    }
    div.stLinkButton > a:hover { background-color: #d92654 !important; opacity: 0.8; }
    </style>
    """, unsafe_allow_stdio=True)

# 3. LINKS (Atualize o URL_FORM quando criar o novo)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIz3YX4UyzZfg6d03AiQ-EyHifW1ezl8gh-3jJUKZjnBLhi0bYEYTVjtu-ag0QnW0QyzCkhgsKs467/pub?gid=1785346654&single=true&output=csv"
URL_FORM = "https://forms.gle/zMyh8ZWvZ4mYSxmu7"

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = [c.strip() for c in df.columns]
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        df['Erros'] = df['Questões Resolvidas'] - df['Acertos']
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

# 4. HEADER PROFISSIONAL
col_tit, col_btn = st.columns([3, 1])
with col_tit:
    st.title("Performance de Estudos")
with col_btn:
    st.link_button("Registrar Novo Estudo", URL_FORM, use_container_width=True)

if df_raw.empty:
    st.info("Aguardando sincronização com a planilha...")
else:
    # --- FILTROS LATERAIS (LIMPÍSSIMOS) ---
    st.sidebar.markdown("### Filtros de Visualização")
    opcoes_atv = ["Todas as Atividades"] + sorted(list(df_raw['Tipo de Atividade'].unique()))
    filtro_atv = st.sidebar.selectbox("Tipo de Atividade", opcoes_atv)
    
    df = df_raw if filtro_atv == "Todas as Atividades" else df_raw[df_raw['Tipo de Atividade'] == filtro_atv]

    # --- MÉTRICAS DE TOPO ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Questões", int(df['Questões Resolvidas'].sum()))
    m2.metric("Acertos", int(df['Acertos'].sum()))
    aproveitamento = (df['Acertos'].sum() / df['Questões Resolvidas'].sum() * 100) if df['Questões Resolvidas'].sum() > 0 else 0
    m3.metric("Aproveitamento", f"{aproveitamento:.1f}%")
    m4.metric("Tempo de Estudo", f"{df['Tempo de Estudo em Minutos'].sum() / 60:.1f}h")

    st.markdown("---")

    # --- PALETA DE CORES ---
    cores_pink_scale = ['#FF2E63', '#08D9D6', '#6A2C70', '#B83B5E', '#252A34']

    # --- LINHA DE GRÁFICOS 1 ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Distribuição por Grande Área")
        fig_pie = px.pie(df, values='Questões Resolvidas', names='Grande Área', hole=0.5,
                         color_discrete_sequence=cores_pink_scale)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with g2:
        st.subheader("Relação Acertos vs Erros")
        resumo = df.groupby('Grande Área')[['Acertos', 'Erros']].sum().reset_index()
        fig_bar = px.bar(resumo, x='Grande Área', y=['Acertos', 'Erros'], barmode='group',
                         color_discrete_map={'Acertos': '#08D9D6', 'Erros': '#FF2E63'})
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- LINHA DE GRÁFICOS 2 ---
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("Evolução Diária de Performance")
        evol = df.groupby('Data')[['Questões Resolvidas', 'Acertos']].sum().reset_index()
        fig_line = px.line(evol, x='Data', y=['Questões Resolvidas', 'Acertos'], markers=True,
                           color_discrete_sequence=['#FF2E63', '#08D9D6'])
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_line, use_container_width=True)

    with g4:
        st.subheader("Temas com Menor Aproveitamento")
        temas = df.groupby('Tema').agg({'Questões Resolvidas': 'sum', 'Erros': 'sum'}).reset_index()
        temas['Taxa de Erro'] = (temas['Erros'] / temas['Questões Resolvidas'])
        top_erros = temas.sort_values('Taxa de Erro', ascending=False).head(5)
        fig_tema = px.bar(top_erros, x='Taxa de Erro', y='Tema', orientation='h', color_discrete_sequence=['#FF2E63'])
        fig_tema.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_tema, use_container_width=True)
