import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Performance de Estudos", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS PARA APARÊNCIA PREMIUM (PINK & DARK)
st.markdown("""
    <style>
    /* Fundo e Fontes */
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FF2E63 !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    
    /* Customização de métricas */
    [data-testid="stMetricLabel"] { color: #AEB2B7 !important; font-size: 1rem !important; }
    [data-testid="stMetricValue"] { color: #08D9D6 !important; font-size: 1.8rem !important; }
    
    /* Botão de Registro */
    div.stLinkButton > a {
        background-color: #FF2E63 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem !important;
        text-decoration: none !important;
        font-weight: bold !important;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        transition: 0.3s;
    }
    div.stLinkButton > a:hover { background-color: #d92654 !important; transform: scale(1.02); }
    
    /* Ajustes Mobile */
    @media (max-width: 640px) {
        [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LINKS CONFIGURADOS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIz3YX4UyzZfg6d03AiQ-EyHifW1ezl8gh-3jJUKZjnBLhi0bYEYTVjtu-ag0QnW0QyzCkhgsKs467/pub?gid=1785346654&single=true&output=csv"
URL_FORM = "https://forms.gle/zMyh8ZWvZ4mYSxmu7"

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL_CSV)
        # Limpa espaços nos nomes das colunas
        df.columns = [c.strip() for c in df.columns]
        # Converte Data
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        # Cria colunas de cálculo
        df['Erros'] = df['Questões Resolvidas'] - df['Acertos']
        df['Taxa de Erro'] = (df['Erros'] / df['Questões Resolvidas']).fillna(0)
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

# 4. HEADER COM BOTÃO PROFISSIONAL
col_tit, col_btn = st.columns([3, 1])
with col_tit:
    st.title("Performance de Estudos")
with col_btn:
    st.link_button("Registrar Novo Estudo", URL_FORM, use_container_width=True)

if df_raw.empty:
    st.warning("Aguardando dados... Certifique-se de que a planilha possui ao menos um registro e que o link CSV está correto.")
else:
    # --- FILTROS LATERAIS (SELECTBOX PARA MAIOR LIMPEZA) ---
    st.sidebar.markdown("### Navegação")
    opcoes_atv = ["Todas as Atividades"] + sorted(list(df_raw['Tipo de Atividade'].unique()))
    filtro_atv = st.sidebar.selectbox("Filtrar Tipo", opcoes_atv)
    
    df = df_raw if filtro_atv == "Todas as Atividades" else df_raw[df_raw['Tipo de Atividade'] == filtro_atv]

    # --- MÉTRICAS DE IMPACTO ---
    m1, m2, m3, m4 = st.columns(4)
    q_total = df['Questões Resolvidas'].sum()
    a_total = df['Acertos'].sum()
    aprov = (a_total / q_total * 100) if q_total > 0 else 0
    tempo = df['Tempo de Estudo em Minutos'].sum() / 60

    m1.metric("Questões", int(q_total))
    m2.metric("Acertos", int(a_total))
    m3.metric("Aproveitamento", f"{aprov:.1f}%")
    m4.metric("Tempo Total", f"{tempo:.1f}h")

    st.markdown("---")

    # --- CORES DO DASHBOARD ---
    paleta_pink = ['#FF2E63', '#08D9D6', '#6A2C70', '#B83B5E', '#252A34']

    # --- LINHA 1 DE GRÁFICOS ---
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Questões por Área")
        fig_pie = px.pie(df, values='Questões Resolvidas', names='Grande Área', 
                         hole=0.5, color_discrete_sequence=paleta_pink)
        fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    with g2:
        st.subheader("Relação Acertos vs Erros")
        resumo = df.groupby('Grande Área')[['Acertos', 'Erros']].sum().reset_index()
        fig_bar = px.bar(resumo, x='Grande Área', y=['Acertos', 'Erros'], 
                         barmode='group', color_discrete_map={'Acertos': '#08D9D6', 'Erros': '#FF2E63'})
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- LINHA 2 DE GRÁFICOS ---
    g3, g4 = st.columns(2)

    with g3:
        st.subheader("Temas com Maior Taxa de Erro")
        # Agrupa por tema e calcula média de erro
        temas_erro = df.groupby('Tema')['Taxa de Erro'].mean().sort_values(ascending=False).head(5).reset_index()
        fig_tema = px.bar(temas_erro, x='Taxa de Erro', y='Tema', orientation='h', 
                          color_discrete_sequence=['#FF2E63'])
        fig_tema.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                               xaxis_tickformat='.0%')
        st.plotly_chart(fig_tema, use_container_width=True)

    with g4:
        st.subheader("Evolução Temporal")
        evol = df.groupby('Data')[['Questões Resolvidas', 'Acertos']].sum().reset_index()
        fig_line = px.line(evol, x='Data', y=['Questões Resolvidas', 'Acertos'], 
                           markers=True, color_discrete_sequence=['#FF2E63', '#08D9D6'])
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white",
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_line, use_container_width=True)
