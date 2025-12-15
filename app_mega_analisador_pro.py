import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------
# 1. CARREGAMENTO DE DADOS (ARQUIVO LOCAL ESTÁVEL)
# ----------------------------------------------------
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
# 3. FUNÇÃO DE ANÁLISE DE ATRASO
# ----------------------------------------------------

def calcular_atraso(df):
    """Calcula quantos concursos se passaram desde a última vez que cada dezena foi sorteada."""
    
    ultimo_concurso = df['Concurso'].max()
    
    atraso_data = []
    
    # Itera por todas as dezenas possíveis (1 a 60)
    for dezena in range(1, 61):
        # Verifica em qual concurso a dezena apareceu pela última vez
        cols_dezenas = [f'Bola{i}' for i in range(1, 7)]
        
        # Filtra o DataFrame para concursos onde a dezena foi sorteada
        df_dezena = df[df[cols_dezenas].eq(dezena).any(axis=1)]
        
        if not df_dezena.empty:
            # Pega o número do último concurso em que ela apareceu
            ultimo_sorteio = df_dezena['Concurso'].max()
            # O atraso é o concurso atual menos o último sorteio
            atraso = int(ultimo_concurso - ultimo_sorteio)
        else:
            # Se nunca foi sorteada (improvável), o atraso é o último concurso
            atraso = int(ultimo_concurso) 

        atraso_data.append({'Dezena': dezena, 'Atraso': atraso})
    
    return pd.DataFrame(atraso_data)

# ----------------------------------------------------
# 4. ANÁLISES E VISUALIZAÇÕES
# ----------------------------------------------------

# Seção de Frequência das Dezenas
st.header("Análise de Frequência das Dezenas")
st.write("Verifique quais dezenas foram mais sorteadas na história.")

# ... (Seu código de frequência original) ...
cols_dezenas = [f'Bola{i}' for i in range(1, 7)]
frequencia = df[cols_dezenas].stack().value_counts().reset_index()
frequencia.columns = ['Dezena', 'Frequência']
frequencia['Dezena'] = frequencia['Dezena'].astype(int) 
frequencia = frequencia.sort_values(by='Dezena')

fig_freq = px.bar(
    frequencia, 
    x='Dezena', 
    y='Frequência', 
    title='Frequência Absoluta das Dezenas',
    labels={'Dezena': 'Dezena Sorteada', 'Frequência': 'Total de Vezes Sorteadas'},
    text='Frequência'
)
fig_freq.update_traces(marker_color='#008000') 
st.plotly_chart(fig_freq, use_container_width=True)

st.markdown("---") # Separador

# Seção de Atraso das Dezenas (NOVO RECURSO)
st.header("⏳ Análise de Atraso das Dezenas")
st.write("Dezenas com maior atraso (em concursos) são as que não são sorteadas há mais tempo.")

df_atraso = calcular_atraso(df)

# Ordena o DataFrame pelo atraso (do maior para o menor)
df_atraso_ordenado = df_atraso.sort_values(by='Atraso', ascending=False)

fig_atraso = px.bar(
    df_atraso_ordenado,
    x='Dezena',
    y='Atraso',
    title='Atraso Atual das Dezenas (em Concursos)',
    labels={'Dezena': 'Dezena', 'Atraso': 'Concursos em Atraso'},
    text='Atraso'
)
fig_atraso.update_traces(marker_color='#FF5733') # Cor Laranja/Vermelha para indicar atraso
st.plotly_chart(fig_atraso, use_container_width=True)


# ----------------------------------------------------
# 5. EXIBIÇÃO DE DADOS BRUTOS (Opcional)
# ----------------------------------------------------
with st.expander("Ver Dados Brutos (Histórico)"):
    st.dataframe(df)
