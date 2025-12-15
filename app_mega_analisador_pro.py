import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. CARREGAMENTO DE DADOS (ARQUIVO LOCAL TEMPORÁRIO)
# ----------------------------------------------------
# Usamos cache para que o Streamlit não precise ler o arquivo do disco toda vez
@st.cache_data 
def load_data():
    """Carrega o histórico da Mega-Sena do arquivo Excel local."""
    try:
        # Lendo o arquivo Excel que está no seu repositório
        df = pd.read_excel('MegaSena.xlsx')
        
        # Garantindo que as colunas de dezenas e concurso sejam numéricas
        cols_dezenas = [f'Bola{i}' for i in range(1, 7)]
        df[cols_dezenas] = df[cols_dezenas].apply(pd.to_numeric, errors='coerce')
        df['Concurso'] = pd.to_numeric(df['Concurso'], errors='coerce')
        
        return df
    
    except Exception as e:
        # Mensagem de erro se o arquivo não for encontrado ou estiver corrompido
        st.error(f"⚠️ Erro ao carregar o arquivo MegaSena.xlsx: Verifique se ele está no repositório.")
        st.stop()
        return None

df = load_data()

if df is not None:
    st.sidebar.success(f"Dados carregados do arquivo local! Último Concurso: {df['Concurso'].max()}")


# ----------------------------------------------------
# 2. CONFIGURAÇÃO DA PÁGINA E CABEÇALHO
# ----------------------------------------------------
st.set_page_config(
    page_title="Mega-Sena PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💰 Analisador Mega-Sena PRO: Análises Completas")
st.markdown("---")

# ----------------------------------------------------
# 3. ANÁLISES E VISUALIZAÇÕES
# ----------------------------------------------------

# Seção de Frequência das Dezenas
st.header("Análise de Frequência das Dezenas")
st.write("Verifique quais dezenas foram mais sorteadas na história.")

# Conta a frequência de cada dezena (bolas 1 a 6)
cols_dezenas = [f'Bola{i}' for i in range(1, 7)]
frequencia = df[cols_dezenas].stack().value_counts().reset_index()
frequencia.columns = ['Dezena', 'Frequência']
frequencia['Dezena'] = frequencia['Dezena'].astype(int) 

# Ordena pela dezena (1 a 60) para o gráfico
frequencia = frequencia.sort_values(by='Dezena')

# Cria o gráfico de barras
fig = px.bar(
    frequencia, 
    x='Dezena', 
    y='Frequência', 
    title='Frequência Absoluta das Dezenas',
    labels={'Dezena': 'Dezena Sorteada', 'Frequência': 'Total de Vezes Sorteadas'},
    text='Frequência'
)
fig.update_traces(marker_color='#008000') 
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 4. EXIBIÇÃO DE DADOS BRUTOS (Opcional)
# ----------------------------------------------------
with st.expander("Ver Dados Brutos (Histórico)"):
    st.dataframe(df)
