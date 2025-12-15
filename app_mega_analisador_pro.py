import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. CARREGAMENTO AUTOMÁTICO DE DADOS (AUTOMAÇÃO CORRIGIDA)
# ----------------------------------------------------
@st.cache_data(ttl=3600) # Armazena o dado em cache por 1 hora
def load_data():
    """Baixa o histórico completo da Mega-Sena da internet e retorna o DataFrame."""
    
    # NOVA URL MAIS ESTÁVEL
    URL_DADOS = 'https://raw.githubusercontent.com/devasc-public/projeto-mega-sena/main/d_megasena.csv' 
    
    try:
        # Baixa o conteúdo do CSV (sem precisar do arquivo Excel local)
        # Note que o separador e a codificação mudam um pouco para este novo arquivo
        df = pd.read_csv(URL_DADOS, sep=',', encoding='utf-8')
        
        # O novo CSV usa colunas D1, D2, D3, D4, D5, D6, vamos renomeá-las para manter a compatibilidade
        # E garantir que estejam como números inteiros
        cols_originais = [f'D{i}' for i in range(1, 7)]
        cols_novas = [f'Bola{i}' for i in range(1, 7)]
        
        # Renomeia as colunas e converte para numérico
        df = df.rename(columns=dict(zip(cols_originais, cols_novas)))
        df[cols_novas] = df[cols_novas].apply(pd.to_numeric, errors='coerce')
        
        # A coluna de concurso também precisa estar como número inteiro
        df['Concurso'] = pd.to_numeric(df['Concurso'], errors='coerce')
        
        return df
    
    except Exception as e:
        # Se falhar, exibe uma mensagem de erro e interrompe a execução
        st.error(f"⚠️ Erro ao carregar dados online. Por favor, tente novamente mais tarde.")
        st.stop()
        return None

df = load_data()

if df is not None:
    st.sidebar.success(f"Dados atualizados! Último Concurso: {df['Concurso'].max()}")


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
frequencia['Dezena'] = frequencia['Dezena'].astype(int) # Converte para inteiro

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
fig.update_traces(marker_color='#008000') # Cor verde Mega-Sena
st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# 4. EXIBIÇÃO DE DADOS BRUTOS (Opcional)
# ----------------------------------------------------
with st.expander("Ver Dados Brutos (Histórico)"):
    st.dataframe(df)
