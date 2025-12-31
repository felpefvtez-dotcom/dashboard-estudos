import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página
st.set_page_config(page_title="Dashboard Maria Eduarda", layout="wide", page_icon="🩺")

# Link que você gerou (já inserido no código)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTIz3YX4UyzZfg6d03AiQ-EyHifW1ezl8gh-3jJUKZjnBLhi0bYEYTVjtu-ag0QnW0QyzCkhgsKs467/pub?output=csv"

@st.cache_data(ttl=60) # Atualiza os dados a cada 1 minuto
def load_data():
    df = pd.read_csv(URL_CSV)
    # Se o Google Forms adicionou a coluna 'Carimbo de data/hora', vamos ignorá-la ou ajustá-la
    # O código abaixo tenta identificar as colunas por ordem para evitar erros de nome
    return df

st.title("📊 Performance de Estudos - Residência Médica")

try:
    df = load_data()
    
    # --- TRATAMENTO DE DADOS ---
    # Convertendo data para formato legível
    col_data = df.columns[1] # Geralmente a 2ª coluna é a data
    df[col_data] = pd.to_datetime(df[col_data])
    
    # Criando coluna de Erros caso não exista
    # Assumindo: [1]Data, [2]Tipo, [3]Área, [4]Tema, [5]Resolvidas, [6]Acertos, [7]Tempo
    df['Erros'] = df.iloc[:, 5] - df.iloc[:, 6] 

    # --- SIDEBAR (FILTROS) ---
    st.sidebar.header("Filtros")
    tipos = st.sidebar.multiselect("Tipo de Atividade", df.iloc[:, 2].unique(), default=df.iloc[:, 2].unique())
    df_filtered = df[df.iloc[:, 2].isin(tipos)]

    # --- DASHBOARD ---
    # KPIs Gerais
    c1, c2, c3, c4 = st.columns(4)
    total_q = df_filtered.iloc[:, 5].sum()
    total_a = df_filtered.iloc[:, 6].sum()
    total_e = df_filtered['Erros'].sum()
    total_t = df_filtered.iloc[:, 7].sum() / 60

    c1.metric("Total Questões", int(total_q))
    c2.metric("Total Acertos", int(total_a), delta=f"{int(total_a)} ✅")
    c3.metric("Aproveitamento", f"{(total_a/total_q)*100:.1f}%" if total_q > 0 else "0%")
    c4.metric("Tempo Total", f"{total_t:.1f}h")

    st.divider()

    col_esq, col_dir = st.columns(2)

    # Gráfico 1: Performance por Área
    perf_area = df_filtered.groupby(df_filtered.columns[3])[[df_filtered.columns[6], 'Erros']].sum().reset_index()
    fig_area = px.bar(perf_area, x=df_filtered.columns[3], y=[df_filtered.columns[6], 'Erros'], 
                     title="Acertos vs Erros por Área", barmode='group',
                     color_discrete_sequence=['#2ecc71', '#e74c3c'])
    col_esq.plotly_chart(fig_area, use_container_width=True)

    # Gráfico 2: Evolução no Tempo
    evol = df_filtered.groupby(col_data)[[df_filtered.columns[5], df_filtered.columns[6]]].sum().reset_index()
    fig_evol = px.line(evol, x=col_data, y=[df_filtered.columns[5], df_filtered.columns[6]], 
                      title="Evolução Diária", markers=True)
    col_dir.plotly_chart(fig_evol, use_container_width=True)

    # Top 5 Temas com mais erros
    st.subheader("⚠️ Top 5 Temas para Revisar (Mais Erros)")
    top_erros = df_filtered.groupby(df_filtered.columns[4])['Erros'].sum().sort_values(ascending=False).head(5)
    st.table(top_erros)

except Exception as e:
    st.error("Aguardando os primeiros dados serem inseridos no formulário...")
    st.info("Certifique-se de que o formulário foi preenchido pelo menos uma vez.")