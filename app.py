import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard Medicina - Maria Eduarda", layout="wide")

# Link direto da sua planilha (já configurado)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIz3YX4UyzZfg6d03AiQ-EyHifW1ezl8gh-3jJUKZjnBLhi0bYEYTVjtu-ag0QnW0QyzCkhgsKs467/pub?gid=1785346654&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL_CSV)
        # Limpeza de nomes de colunas
        df.columns = [c.strip() for c in df.columns]
        # Converte Data para formato datetime
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
        # Cria coluna de Erros
        df['Erros'] = df['Questões Resolvidas'] - df['Acertos']
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df_raw = load_data()

# Título Principal
st.title("🩺 Performance de Estudos - Residência Médica")

if df_raw.empty:
    st.info("Aguardando o carregamento dos dados da planilha...")
else:
    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("Filtros")
    atividades = st.sidebar.multiselect(
        "Tipo de Atividade",
        options=df_raw['Tipo de Atividade'].unique(),
        default=df_raw['Tipo de Atividade'].unique()
    )
    
    # Filtrando os dados
    df = df_raw[df_raw['Tipo de Atividade'].isin(atividades)]

    # --- LINHA 1: MÉTRICAS (KPIs) ---
    total_q = df['Questões Resolvidas'].sum()
    total_a = df['Acertos'].sum()
    aproveitamento = (total_a / total_q * 100) if total_q > 0 else 0
    tempo_total = df['Tempo de Estudo em Minutos'].sum() / 60

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Questões", f"{total_q}")
    c2.metric("Total Acertos", f"{total_a}")
    c3.metric("Aproveitamento", f"{aproveitamento:.1f}%")
    c4.metric("Tempo Total", f"{tempo_total:.1f}h")

    st.markdown("---")

    # --- LINHA 2: GRÁFICOS DE ÁREA E ERROS X ACERTOS ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("TOTAL DE QUESTÕES RESOLVIDAS")
        fig_pie = px.pie(df, values='Questões Resolvidas', names='Grande Área', 
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("RELAÇÃO ERROS X ACERTOS")
        resumo_area = df.groupby('Grande Area' if 'Grande Area' in df.columns else 'Grande Área').agg({'Acertos': 'sum', 'Erros': 'sum'}).reset_index()
        fig_bar = px.bar(resumo_area, x='Grande Área', y=['Acertos', 'Erros'], 
                         barmode='stack', color_discrete_map={'Acertos': '#1f77b4', 'Erros': '#d62728'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- LINHA 3: TOP TEMAS E EVOLUÇÃO ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("TOP 5 TEMAS COM MAIOR TAXA DE ERRO")
        # Cálculo de taxa de erro por tema
        temas = df.groupby('Tema').agg({'Questões Resolvidas': 'sum', 'Erros': 'sum'}).reset_index()
        temas['Taxa de Erro'] = temas['Erros'] / temas['Questões Resolvidas']
        top_erros = temas.sort_values(by='Taxa de Erro', ascending=False).head(5)
        
        fig_tema = px.bar(top_erros, x='Taxa de Erro', y='Tema', orientation='h',
                          color_discrete_sequence=['#ef553b'])
        fig_tema.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_tema, use_container_width=True)

    with col4:
        st.subheader("EVOLUÇÃO TEMPORAL")
        evolucao = df.groupby('Data').agg({'Questões Resolvidas': 'sum', 'Acertos': 'sum'}).reset_index().sort_values('Data')
        fig_line = px.line(evolucao, x='Data', y=['Questões Resolvidas', 'Acertos'], 
                           markers=True, color_discrete_sequence=['#1f77b4', '#d62728'])
        st.plotly_chart(fig_line, use_container_width=True)
