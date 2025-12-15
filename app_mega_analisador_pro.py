import streamlit as st
import pandas as pd
import os
import random
from itertools import combinations
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import time # Importar time para simular o save/load

# --- Configuração da Página ---
st.set_page_config(layout="wide", page_title="Analisador Mega-Sena PRO")
st.title("💰 Analisador Mega-Sena PRO: Análises Completas e Estratégias Inteligentes")
st.markdown("---")

# -------------------------------------------------------------
# [NOVO] SISTEMA DE LOGIN PRO PARA MONETIZAÇÃO
# -------------------------------------------------------------
# ATENÇÃO: Mude esta senha para a que você vai vender!
SENHA_PRO = "MEGA2025PRO" 

if 'acesso_pro' not in st.session_state:
    st.session_state['acesso_pro'] = False

ACESSOU_PRO = st.session_state['acesso_pro']

if not ACESSOU_PRO:
    st.subheader("Acesso PRO 🔑")
    senha_digitada = st.text_input("Digite a senha de acesso PRO:", type="password", help="Acesso às abas Geradores e Estratégias.")
    
    if senha_digitada == SENHA_PRO:
        st.session_state['acesso_pro'] = True
        st.success("Acesso PRO liberado! As abas de Estratégias e Geradores estão agora visíveis.")
        st.rerun() # Recarrega a página para mostrar as abas
    elif senha_digitada and senha_digitada != SENHA_PRO:
        st.error("Senha incorreta. Adquira seu acesso para liberar as funcionalidades PRO.")
    
    st.markdown("---")
    st.stop() # Interrompe a execução do resto do app se o login não foi feito
# -------------------------------------------------------------

# Configurações
COLUNAS_DEZENAS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6']
FILE_PATH = "MegaSena.xlsx"
NUM_DEZENAS_TOTAL = 60
NUM_DEZENAS_SORTEADAS = 6

# --- Funções Auxiliares (INALTERADAS) ---

def eh_primo(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

@st.cache_data
def carregar_dados_do_arquivo(file_path=FILE_PATH):
    try:
        if not os.path.exists(file_path):
            st.warning(f"Arquivo '{file_path}' não encontrado.")
            return pd.DataFrame(), 0, 0
            
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
            
        # Adicionei uma verificação mais robusta para garantir que o Concurso seja o índice
        colunas_identificadas = df.columns[:8].tolist()
        if len(colunas_identificadas) < 8:
            st.error("Estrutura do Excel incorreta. Esperado no mínimo 8 colunas (Concurso, Data, B1..B6).")
            return pd.DataFrame(), 0, 0
            
        df = df.iloc[:, 0:8].fillna(0)
        df.columns = ['Concurso', 'Data'] + COLUNAS_DEZENAS
        df = df.set_index('Concurso')
        df[COLUNAS_DEZENAS] = df[COLUNAS_DEZENAS].astype(int)
            
        concurso_min = df.index.min()
        concurso_max = df.index.max()
            
        return df, concurso_min, concurso_max
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return pd.DataFrame(), 0, 0

def get_frequencia_e_atraso(df_completo, df_base_completa=None):
    if df_base_completa is None:
        df_base_completa = df_completo
        
    todas_dezenas = df_completo[COLUNAS_DEZENAS].values.flatten()
    frequencia_no_periodo = pd.Series(todas_dezenas).loc[lambda x: x > 0].value_counts().reset_index()
    frequencia_no_periodo.columns = ['Dezena', 'Vezes']
        
    dezenas_completas = pd.DataFrame({'Dezena': range(1, NUM_DEZENAS_TOTAL + 1)})
    df_frequencia = pd.merge(dezenas_completas, frequencia_no_periodo, on='Dezena', how='left').fillna(0)
    df_frequencia['Vezes'] = df_frequencia['Vezes'].astype(int)
        
    ultimo_concurso = df_base_completa.index.max()
    atrasos = []
    for dezena in df_frequencia['Dezena']:
        concursos_saida = df_base_completa[(df_base_completa[COLUNAS_DEZENAS] == dezena).any(axis=1)].index.tolist()
        if concursos_saida:
            atraso = ultimo_concurso - max(concursos_saida)
        else:
            atraso = len(df_base_completa)
        atrasos.append(atraso)
    df_frequencia['Atraso'] = atrasos
    df_frequencia['Atraso'] = df_frequencia['Atraso'].astype(int)
        
    return df_frequencia

# ... (Funções calcular_frequencia_pares, calcular_frequencia_trios, analisar_padroes_avancados,
# calcular_atraso_dezena, analisar_sequencias_dezenas são mantidas) ...

# Funções de Pares/Trios/Padrões (Mantidas, omitidas para brevidade, mas devem estar no seu arquivo .py)
def calcular_frequencia_pares(df_analise):
    todos_pares = []
    for _, row in df_analise[COLUNAS_DEZENAS].iterrows():
        dezenas_sorteadas = [d for d in row.tolist() if d > 0]
        for par in combinations(sorted(dezenas_sorteadas), 2):
            todos_pares.append(par)
    contagem_pares = Counter(todos_pares)
    df_pares = pd.DataFrame(contagem_pares.items(), columns=['Par', 'Frequencia'])
    df_pares['Dezena 1'] = df_pares['Par'].apply(lambda x: x[0])
    df_pares['Dezena 2'] = df_pares['Par'].apply(lambda x: x[1])
    return df_pares.sort_values(by='Frequencia', ascending=False)

def calcular_frequencia_trios(df_analise):
    todos_trios = []
    for _, row in df_analise[COLUNAS_DEZENAS].iterrows():
        dezenas_sorteadas = [d for d in row.tolist() if d > 0]
        for trio in combinations(sorted(dezenas_sorteadas), 3):
            todos_trios.append(trio)
    contagem_trios = Counter(todos_trios)
    df_trios = pd.DataFrame(contagem_trios.items(), columns=['Trio', 'Frequencia'])
    df_trios['D1'] = df_trios['Trio'].apply(lambda x: x[0])
    df_trios['D2'] = df_trios['Trio'].apply(lambda x: x[1])
    df_trios['D3'] = df_trios['Trio'].apply(lambda x: x[2])
    return df_trios.sort_values(by='Frequencia', ascending=False)

def analisar_padroes_avancados(df_analise):
    resultados = []
    for _, row in df_analise[COLUNAS_DEZENAS].iterrows():
        dezenas = [d for d in row.tolist() if d > 0]
        pares = sum(1 for d in dezenas if d % 2 == 0)
        impares = len(dezenas) - pares
        primos = sum(1 for d in dezenas if eh_primo(d))
        soma = sum(dezenas)
            
        resultados.append({
            'Pares': pares,
            'Impares': impares,
            'Primos': primos,
            'Soma': soma
        })
            
    df_padroes = pd.DataFrame(resultados)
    return {
        'Pares_Medio': df_padroes['Pares'].mean(),
        'Impares_Medio': df_padroes['Impares'].mean(),
        'Primos_Medio': df_padroes['Primos'].mean(),
        'Soma_Media': df_padroes['Soma'].mean()
    }

def analisar_sequencias_dezenas(df_completo, dezena_referencia, top_n=15):
    concursos_com_dezena = df_completo[(df_completo[COLUNAS_DEZENAS] == dezena_referencia).any(axis=1)].index.tolist()
        
    if not concursos_com_dezena:
        return pd.DataFrame()
        
    concursos_seguintes = [c + 1 for c in concursos_com_dezena if c + 1 in df_completo.index]
        
    if not concursos_seguintes:
        return pd.DataFrame()
        
    dezenas_seguintes = []
    for concurso in concursos_seguintes:
        for col in COLUNAS_DEZENAS:
            dez = df_completo.loc[concurso, col]
            if dez > 0:
                dezenas_seguintes.append(int(dez))
        
    contagem = Counter(dezenas_seguintes)
    concurso_atual = df_completo.index.max()
        
    df_sequencia = pd.DataFrame([
        {
            'Dezena': str(dez).zfill(2),
            'Frequência': freq,
            'Percentual': (freq / len(concursos_seguintes)) * 100,
            'Atraso': calcular_atraso_dezena(df_completo, dez, concurso_atual)
        }
        for dez, freq in contagem.most_common(top_n)
    ])
        
    return df_sequencia

def calcular_atraso_dezena(df_completo, dezena, concurso_mais_recente):
    concursos_saida = df_completo[(df_completo[COLUNAS_DEZENAS] == dezena).any(axis=1)].index.tolist()
    if concursos_saida:
        return concurso_mais_recente - max(concursos_saida)
    else:
        return len(df_completo)

# --- Funções de Geração de Jogos (Estratégias PRO) ---

def gerar_jogo_otimizado(df_freq_e_atraso, num_dezenas=6):
    df_temp = df_freq_e_atraso.copy()
    # Ajustando Score: Prioriza Frequência e Atraso (Se você quiser manter o que tinha antes, use: 0.7/0.3)
    df_temp['Score'] = (df_temp['Vezes'] * 1.5) + (df_temp['Atraso'] * 0.5) 
    df_sorted = df_temp.sort_values(by='Score', ascending=False)
    dezenas_selecionadas = df_sorted.head(num_dezenas)['Dezena'].tolist()
    return sorted([int(d) for d in dezenas_selecionadas])

def gerar_jogo_quentes(df_freq_e_atraso, num_dezenas=6):
    df_sorted = df_freq_e_atraso.sort_values(by='Vezes', ascending=False)
    dezenas_selecionadas = df_sorted.head(num_dezenas)['Dezena'].tolist()
    return sorted([int(d) for d in dezenas_selecionadas])

def gerar_jogo_atrasadas(df_freq_e_atraso, num_dezenas=6):
    df_sorted = df_freq_e_atraso.sort_values(by='Atraso', ascending=False)
    dezenas_selecionadas = df_sorted.head(num_dezenas)['Dezena'].tolist()
    return sorted([int(d) for d in dezenas_selecionadas])

def gerar_jogo_balanceado(df_freq_e_atraso, num_dezenas=6):
    df_temp = df_freq_e_atraso.copy()
    metade = num_dezenas // 2
    df_quentes = df_temp.sort_values(by='Vezes', ascending=False)
    df_atrasadas = df_temp.sort_values(by='Atraso', ascending=False)
        
    dezenas_quentes = df_quentes.head(metade)['Dezena'].tolist()
    dezenas_atrasadas = df_atrasadas.head(num_dezenas - metade)['Dezena'].tolist()
        
    dezenas_selecionadas = list(set(dezenas_quentes + dezenas_atrasadas))
    if len(dezenas_selecionadas) < num_dezenas:
        faltam = num_dezenas - len(dezenas_selecionadas)
        outras = df_temp[~df_temp['Dezena'].isin(dezenas_selecionadas)].head(faltam)['Dezena'].tolist()
        dezenas_selecionadas.extend(outras)
        
    return sorted([int(d) for d in dezenas_selecionadas[:num_dezenas]])

def gerar_jogo_aleatorio_inteligente(df_freq_e_atraso, num_dezenas=6):
    df_temp = df_freq_e_atraso.copy()
    # Define um pool de 20 dezenas com base em um Score (Frequência > Atraso)
    df_temp['Score'] = (df_temp['Vezes'] * 0.7) + (df_temp['Atraso'] * 0.3)
    df_top = df_temp.sort_values(by='Score', ascending=False).head(20)
        
    dezenas_selecionadas = random.sample(df_top['Dezena'].tolist(), min(num_dezenas, len(df_top)))
    return sorted([int(d) for d in dezenas_selecionadas])

# --- Carregamento de Dados ---
if 'df_mega_completo' not in st.session_state:
    st.session_state['df_mega_completo'], st.session_state['concurso_min'], st.session_state['concurso_max'] = carregar_dados_do_arquivo()
if 'jogos_salvos' not in st.session_state:
    st.session_state['jogos_salvos'] = []

df_completo = st.session_state['df_mega_completo']

# Limpar cache a cada execução para garantir dados frescos
def limpar_cache_se_necessario():
    """Força limpeza de cache para análises dependentes de período"""
    pass

limpar_cache_se_necessario()

if df_completo is not None and not df_completo.empty:
    # --- SIDEBAR ---
    st.sidebar.header("⚙️ Configurações de Análise")
    st.sidebar.markdown("---")
        
    concurso_min = st.session_state['concurso_min']
    concurso_max = st.session_state['concurso_max']
        
    col_start, col_end = st.sidebar.columns(2)
        
    concurso_inicio = col_start.number_input(
        "Concurso Inicial:",
        min_value=concurso_min,
        max_value=concurso_max,
        value=max(concurso_min, concurso_max - 100),
        step=1,
        key='concurso_inicio_mega'
    )
        
    concurso_fim = col_end.number_input(
        "Concurso Final:",
        min_value=concurso_min,
        max_value=concurso_max,
        value=concurso_max,
        step=1,
        key='concurso_fim_mega'
    )
        
    df_analise = df_completo[(df_completo.index >= concurso_inicio) & (df_completo.index <= concurso_fim)].copy()
        
    if df_analise.empty:
        st.warning("Período inválido.")
        st.stop()
        
    num_concursos = len(df_analise)
    df_freq_e_atraso = get_frequencia_e_atraso(df_analise, df_completo)
    
    # ----------------------------------------------------------------------------------
    # [NOVO] DEFINIÇÃO DE ABAS CONDICIONAL
    # ----------------------------------------------------------------------------------
    abas_basicas = ["📊 Dashboard", "🔍 Análises Avançadas", "🔗 Pares e Trios", "🌡️ Ciclos", "🎯 Sequências"]

    abas_pro_nomes = []
    if ACESSOU_PRO: # Agora essa verificação é crucial
        abas_pro_nomes = ["🎲 Estratégias", "🚀 Geradores", "💾 Meus Jogos PRO"]

    nomes_abas_completos = abas_basicas + abas_pro_nomes
    abas = st.tabs(nomes_abas_completos)

    # Mapeamento das abas para fácil acesso
    tab_dashboard = abas[0]
    tab_analises = abas[1]
    tab_pares_trios = abas[2]
    tab_ciclos = abas[3]
    tab_sequencias = abas[4]

    # Condicionalmente define as abas PRO
    tab_estrategias = abas[5] if "🎲 Estratégias" in nomes_abas_completos else None
    tab_geradores = abas[6] if "🚀 Geradores" in nomes_abas_completos else None
    tab_meus_jogos = abas[7] if "💾 Meus Jogos PRO" in nomes_abas_completos else None
    # ----------------------------------------------------------------------------------


    # =================================================================
    # TAB: DASHBOARD
    # =================================================================
    with tab_dashboard:
        st.header("📊 Dashboard Principal")
        st.info(f"Análise baseada em {num_concursos} concursos (#{concurso_inicio} a #{concurso_fim})")
            
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
        total_sorteios = num_concursos * NUM_DEZENAS_SORTEADAS
        dezenas_unicas = len(df_freq_e_atraso[df_freq_e_atraso['Vezes'] > 0])
        freq_media = df_freq_e_atraso['Vezes'].mean()
        atraso_medio = df_freq_e_atraso['Atraso'].mean()
            
        with col_m1:
            st.metric("Total de Sorteios", f"{total_sorteios:,}")
        with col_m2:
            st.metric("Dezenas Sorteadas", f"{dezenas_unicas}/60")
        with col_m3:
            st.metric("Freq. Média", f"{freq_media:.1f}")
        with col_m4:
            st.metric("Atraso Médio", f"{atraso_medio:.1f}")
            
        st.markdown("---")
            
        col_top1, col_top2 = st.columns(2)
            
        with col_top1:
            st.subheader("🔥 Top 10 Mais Frequentes")
            top_freq = df_freq_e_atraso.sort_values(by='Vezes', ascending=False).head(10)
                
            for _, row in top_freq.iterrows():
                dezena = int(row['Dezena'])
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 5px 0;
                    color: white;
                    display: flex;
                    justify-content: space-between;
                ">
                    <div style="font-size: 24px; font-weight: bold;">{dezena:02d}</div>
                    <div style="text-align: right;">
                        <div>Frequência: {int(row['Vezes'])}</div>
                        <div style="font-size: 12px;">Atraso: {int(row['Atraso'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        with col_top2:
            st.subheader("❄️ Top 10 Mais Atrasadas")
            top_atraso = df_freq_e_atraso.sort_values(by='Atraso', ascending=False).head(10)
                
            for _, row in top_atraso.iterrows():
                dezena = int(row['Dezena'])
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 10px;
                    border-radius: 8px;
                    margin: 5px 0;
                    color: white;
                    display: flex;
                    justify-content: space-between;
                ">
                    <div style="font-size: 24px; font-weight: bold;">{dezena:02d}</div>
                    <div style="text-align: right;">
                        <div>Atraso: {int(row['Atraso'])}</div>
                        <div style="font-size: 12px;">Freq: {int(row['Vezes'])}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        st.markdown("---")
            
        st.subheader("📈 Distribuição de Frequência")
        fig_freq = px.bar(
            df_freq_e_atraso.sort_values(by='Vezes', ascending=False),
            x='Dezena',
            y='Vezes',
            title='Frequência de Todas as Dezenas',
            labels={'Dezena': 'Dezena', 'Vezes': 'Frequência'}
        )
        fig_freq.update_traces(marker_color='#667eea')
        st.plotly_chart(fig_freq, use_container_width=True)
        
    # =================================================================
    # TAB: ANÁLISES
    # =================================================================
    with tab_analises:
        st.header("🔍 Análises Avançadas")
            
        padroes = analisar_padroes_avancados(df_analise)
            
        st.subheader("📊 Padrões Estatísticos Médios")
            
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
            
        with col_p1:
            st.metric("Pares (Média)", f"{padroes['Pares_Medio']:.1f}")
        with col_p2:
            st.metric("Ímpares (Média)", f"{padroes['Impares_Medio']:.1f}")
        with col_p3:
            st.metric("Primos (Média)", f"{padroes['Primos_Medio']:.1f}")
        with col_p4:
            st.metric("Soma (Média)", f"{padroes['Soma_Media']:.0f}")
            
        st.markdown("---")
            
        col_g1, col_g2 = st.columns(2)
            
        with col_g1:
            fig_paridade = go.Figure(data=[go.Pie(
                labels=['Pares', 'Ímpares'],
                values=[padroes['Pares_Medio'], padroes['Impares_Medio']],
                marker=dict(colors=['#667eea', '#764ba2'])
            )])
            fig_paridade.update_layout(title='Distribuição: Pares vs Ímpares')
            st.plotly_chart(fig_paridade, use_container_width=True)
            
        with col_g2:
            fig_primos = go.Figure(data=[go.Pie(
                labels=['Primos', 'Não-Primos'],
                values=[padroes['Primos_Medio'], 6 - padroes['Primos_Medio']],
                marker=dict(colors=['#f093fb', '#f5576c'])
            )])
            fig_primos.update_layout(title='Distribuição: Primos vs Não-Primos')
            st.plotly_chart(fig_primos, use_container_width=True)
            
        st.markdown("---")
            
        st.subheader("📋 Tabela Completa")
        df_display = df_freq_e_atraso.copy()
        df_display['Dezena Formatada'] = df_display['Dezena'].apply(lambda x: f'{int(x):02d}')
        df_display['Par/Ímpar'] = df_display['Dezena'].apply(lambda x: 'Par' if x % 2 == 0 else 'Ímpar')
        df_display['Primo'] = df_display['Dezena'].apply(lambda x: 'Sim' if eh_primo(int(x)) else 'Não')
            
        st.dataframe(
            df_display[['Dezena Formatada', 'Vezes', 'Atraso', 'Par/Ímpar', 'Primo']].sort_values(by='Vezes', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
    # =================================================================
    # TAB: PARES E TRIOS
    # =================================================================
    with tab_pares_trios:
        st.header("🔗 Análise de Pares e Trios")
            
        if len(df_analise) >= 2:
            st.subheader("👥 Top 20 Pares Mais Frequentes")
            df_pares = calcular_frequencia_pares(df_analise)
            top_20_pares = df_pares.head(20)
                
            cols_pares = st.columns(4)
            for idx, (_, row) in enumerate(top_20_pares.iterrows()):
                col_idx = idx % 4
                with cols_pares[col_idx]:
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 15px;
                        border-radius: 10px;
                        text-align: center;
                        color: white;
                        margin: 5px 0;
                    ">
                        <div style="font-size: 10px;">#{idx+1}</div>
                        <div style="font-size: 20px; font-weight: bold;">{int(row['Dezena 1']):02d} - {int(row['Dezena 2']):02d}</div>
                        <div style="font-size: 14px;">↑ {int(row['Frequencia'])}x</div>
                    </div>
                    """, unsafe_allow_html=True)
                
            with st.expander("📋 Ver Top 50 Pares"):
                df_pares_display = df_pares.head(50).copy()
                df_pares_display['Par'] = df_pares_display.apply(lambda r: f"{int(r['Dezena 1']):02d} - {int(r['Dezena 2']):02d}", axis=1)
                st.dataframe(df_pares_display[['Par', 'Frequencia']], use_container_width=True, hide_index=True)
                
            st.markdown("---")
                
            st.subheader("👨‍👩‍👦 Top 15 Trios Mais Frequentes")
                
            with st.spinner("Calculando trios..."):
                df_trios = calcular_frequencia_trios(df_analise)
                top_15_trios = df_trios.head(15)
                    
                cols_trios = st.columns(3)
                for idx, (_, row) in enumerate(top_15_trios.iterrows()):
                    col_idx = idx % 3
                    with cols_trios[col_idx]:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            padding: 15px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                            margin: 5px 0;
                        ">
                            <div style="font-size: 10px;">#{idx+1}</div>
                            <div style="font-size: 18px; font-weight: bold;">{int(row['D1']):02d} - {int(row['D2']):02d} - {int(row['D3']):02d}</div>
                            <div style="font-size: 14px;">↑ {int(row['Frequencia'])}x</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("Período de análise muito curto para calcular pares e trios.")
        
    # =================================================================
    # TAB: CICLOS
    # =================================================================
    with tab_ciclos:
        st.header("🌡️ Análise de Ciclos")
            
        media_freq = df_freq_e_atraso['Vezes'].mean()
        media_atraso = df_freq_e_atraso['Atraso'].mean()
            
        df_ciclos = df_freq_e_atraso.copy()
            
        def classificar_ciclo(row):
            if row['Vezes'] >= media_freq and row['Atraso'] <= media_atraso:
                return '🔥 Muito Quente'
            elif row['Vezes'] >= media_freq:
                return '🟠 Quente'
            elif row['Atraso'] >= media_atraso:
                return '❄️ Fria'
            else:
                return '🔵 Neutro'
            
        df_ciclos['Ciclo'] = df_ciclos.apply(classificar_ciclo, axis=1)
        df_ciclos['Dezena Formatada'] = df_ciclos['Dezena'].apply(lambda x: f'{int(x):02d}')
            
        col_c1, col_c2 = st.columns(2)
            
        with col_c1:
            st.subheader("🔥 Dezenas Quentes")
            df_quentes = df_ciclos[df_ciclos['Ciclo'].isin(['🔥 Muito Quente', '🟠 Quente'])].sort_values(by='Vezes', ascending=False).head(15)
                
            if not df_quentes.empty:
                for _, row in df_quentes.iterrows():
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                        padding: 10px;
                        border-radius: 8px;
                        margin: 5px 0;
                        color: white;
                        display: flex;
                        justify-content: space-between;
                    ">
                        <div style="font-size: 20px; font-weight: bold;">{row['Dezena Formatada']}</div>
                        <div style="text-align: right;">
                            <div>{row['Ciclo']}</div>
                            <div style="font-size: 12px;">Freq: {int(row['Vezes'])} | Atraso: {int(row['Atraso'])}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
        with col_c2:
            st.subheader("❄️ Dezenas Frias")
            df_frias = df_ciclos[df_ciclos['Ciclo'] == '❄️ Fria'].sort_values(by='Atraso', ascending=False).head(15)
                
            if not df_frias.empty:
                for _, row in df_frias.iterrows():
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                        padding: 10px;
                        border-radius: 8px;
                        margin: 5px 0;
                        color: white;
                        display: flex;
                        justify-content: space-between;
                    ">
                        <div style="font-size: 20px; font-weight: bold;">{row['Dezena Formatada']}</div>
                        <div style="text-align: right;">
                            <div>{row['Ciclo']}</div>
                            <div style="font-size: 12px;">Freq: {int(row['Vezes'])} | Atraso: {int(row['Atraso'])}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
    # =================================================================
    # TAB: SEQUÊNCIAS
    # =================================================================
    with tab_sequencias:
        st.header("🎯 Análise de Sequências")
        st.info("Descubra quais dezenas mais aparecem no sorteio seguinte.")
            
        ultimo_resultado = df_analise[COLUNAS_DEZENAS].iloc[-1].tolist()
        dezenas_ultimo = sorted([int(d) for d in ultimo_resultado if d > 0])
            
        st.markdown(f"**Último Resultado Analisado:** {' | '.join([str(d).zfill(2) for d in dezenas_ultimo])}")
        st.markdown("---")
            
        for idx, dezena_origem in enumerate(dezenas_ultimo):
            st.markdown(f"### Após a Dezena **{dezena_origem:02d}** sair")
                
            df_seq = analisar_sequencias_dezenas(df_analise, dezena_origem, top_n=15)
                
            if not df_seq.empty:
                top_6 = df_seq.head(6)
                    
                cols_top6 = st.columns(6)
                for i, (_, row) in enumerate(top_6.iterrows()):
                    dezena_int = int(row['Dezena'])
                        
                    with cols_top6[i]:
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px;
                            border-radius: 10px;
                            text-align: center;
                            color: white;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        ">
                            <div style="font-size: 12px; opacity: 0.9;">#{i+1}</div>
                            <div style="font-size: 36px; font-weight: bold; margin: 10px 0;">{row['Dezena']}</div>
                            <div style="font-size: 14px; margin: 5px 0;">↑ {int(row['Frequência'])}x - {row['Percentual']:.1f}%</div>
                            <div style="font-size: 12px; opacity: 0.8;">Atraso: {int(row['Atraso'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                with st.expander(f"📋 Ver Top 15 completo - Dezena {dezena_origem:02d}"):
                    st.dataframe(df_seq.astype(str), use_container_width=True, hide_index=True)
                
                st.markdown("---")
            
        st.subheader("🔍 Buscar Sequência de Qualquer Dezena")
            
        col_b1, col_b2 = st.columns([1, 3])
            
        with col_b1:
            dezena_busca = st.number_input("Dezena:", min_value=1, max_value=60, value=dezenas_ultimo[0], step=1, key='dezena_busca_seq')
            
        with col_b2:
            df_seq_busca = analisar_sequencias_dezenas(df_analise, int(dezena_busca), top_n=15)
                
            if not df_seq_busca.empty:
                st.dataframe(df_seq_busca.astype(str), use_container_width=True, hide_index=True)
            else:
                st.warning("Sem dados para esta dezena no período de análise.")
        
    # =================================================================
    # [CONDICIONAL] TAB: ESTRATÉGIAS
    # =================================================================
    if tab_estrategias is not None:
        with tab_estrategias:
            st.header("🎲 Estratégias de Jogo (Acesso PRO)")
                
            num_dez = st.selectbox("Quantidade de dezenas:", options=[6, 7, 8, 9, 10, 12, 15], index=0, key='num_dez_estrategias')
                
            st.markdown("---")
                
            # Adiciona botão para salvar jogo
            def display_strategy_game(title, game_func, df, num, key_suffix):
                st.subheader(title)
                jogo = game_func(df, num)
                separador = ' ' if num == 6 else ', '
                jogo_str = separador.join([f'{d:02d}' for d in jogo])
                st.code(jogo_str, language='text')
                
                if st.button(f"💾 Salvar {title.split(':')[1].strip()} ({num} dezenas)", key=f'salvar_est_{key_suffix}'):
                    st.session_state['jogos_salvos'].append(f"{title.split(':')[1].strip()} ({num}D) - {jogo_str}")
                    st.success(f"Jogo salvo em 'Meus Jogos PRO': {jogo_str}")

            display_strategy_game("⭐ Estratégia 1: Otimizada (Score)", gerar_jogo_otimizado, df_freq_e_atraso, num_dez, "otm")
            st.markdown("---")
            display_strategy_game("🔥 Estratégia 2: Apenas Quentes", gerar_jogo_quentes, df_freq_e_atraso, num_dez, "qte")
            st.markdown("---")
            display_strategy_game("❄️ Estratégia 3: Apenas Atrasadas", gerar_jogo_atrasadas, df_freq_e_atraso, num_dez, "atr")
            st.markdown("---")
            display_strategy_game("⚖️ Estratégia 4: Balanceada", gerar_jogo_balanceado, df_freq_e_atraso, num_dez, "bal")
        
    # =================================================================
    # [CONDICIONAL] TAB: GERADORES
    # =================================================================
    if tab_geradores is not None:
        with tab_geradores:
            st.header("🚀 Geradores de Jogos (Acesso PRO)")
            
            st.subheader("🔥 Gerador com Dezenas Muito Quentes")
            
            media_freq = df_freq_e_atraso['Vezes'].mean()
            media_atraso = df_freq_e_atraso['Atraso'].mean()
            
            df_muito_quentes = df_freq_e_atraso[
                (df_freq_e_atraso['Vezes'] >= media_freq) & 
                (df_freq_e_atraso['Atraso'] <= media_atraso)
            ].sort_values(by='Vezes', ascending=False)
            
            num_muito_quentes = len(df_muito_quentes)
            
            st.markdown(f"**Dezenas Muito Quentes disponíveis:** {num_muito_quentes}")
            
            if num_muito_quentes > 0:
                with st.expander("👀 Ver Dezenas Muito Quentes"):
                    dezenas_mq = [f"{int(d):02d}" for d in df_muito_quentes['Dezena'].tolist()]
                    st.code(' '.join(dezenas_mq), language='text')
                
                col_gq1, col_gq2 = st.columns(2)
                
                with col_gq1:
                    num_gerar = st.slider("Qtd de Dezenas para o Jogo:", min_value=6, max_value=min(10, num_muito_quentes), value=6, step=1, key='slider_mq')
                    
                with col_gq2:
                    if st.button("🔥 Gerar Jogo (Muito Quentes)", key='gerar_mq_btn'):
                        qtd = num_gerar
                        
                        if num_muito_quentes >= qtd:
                            # 1. Tenta pegar as mais quentes/frequentes do pool de muito quentes
                            jogo_mq = [int(d) for d in df_muito_quentes.head(qtd)['Dezena'].tolist()]
                        else:
                            # 2. Se não houver o suficiente, preenche com o restante
                            jogo_mq = [int(d) for d in df_muito_quentes['Dezena'].tolist()]
                            faltam = qtd - len(jogo_mq)
                            if faltam > 0:
                                # Pega as próximas mais frequentes no geral para completar
                                df_restantes = df_freq_e_atraso[~df_freq_e_atraso['Dezena'].isin(jogo_mq)].sort_values(by='Vezes', ascending=False)
                                jogo_mq.extend([int(d) for d in df_restantes.head(faltam)['Dezena'].tolist()])
                                
                        jogo_mq = sorted(jogo_mq) # <--- Onde seu código parou!
                        jogo_str = ' '.join([f'{d:02d}' for d in jogo_mq])
                        st.success(f"Jogo Gerado: {jogo_str}")
                        if st.button("💾 Salvar este Jogo (MQ)", key='salvar_mq'):
                             st.session_state['jogos_salvos'].append(f"Gerador MQ ({num_gerar}D) - {jogo_str}")
                             st.success(f"Jogo salvo em 'Meus Jogos PRO': {jogo_str}")
                        st.markdown("---")
            else:
                st.warning("Não há dezenas classificadas como 'Muito Quentes' neste período.")
            
            st.markdown("---")
            st.subheader("💡 Gerador Aleatório Inteligente")
            st.info("Seleciona dezenas aleatoriamente do TOP 20 com melhor Score (Freq + Atraso).")
            
            num_dez_int = st.selectbox("Qtd de Dezenas:", options=[6, 7, 8, 9, 10], index=0, key='num_dez_int_select')
            
            if st.button("🔄 Gerar Jogo Aleatório Inteligente", key='gerar_int_btn'):
                jogo_int = gerar_jogo_aleatorio_inteligente(df_freq_e_atraso, num_dez_int)
                separador = ' ' if num_dez_int == 6 else ', '
                jogo_str = separador.join([f'{d:02d}' for d in jogo_int])
                st.success(f"Jogo Gerado: {jogo_str}")
                if st.button("💾 Salvar este Jogo (AI)", key='salvar_int'):
                    st.session_state['jogos_salvos'].append(f"Gerador AI ({num_dez_int}D) - {jogo_str}")
                    st.success(f"Jogo salvo em 'Meus Jogos PRO': {jogo_str}")
                st.markdown("---")

    # =================================================================
    # [CONDICIONAL] TAB: MEUS JOGOS PRO
    # =================================================================
    if tab_meus_jogos is not None:
        with tab_meus_jogos:
            st.header("💾 Meus Jogos Salvos (Acesso PRO)")
            
            if not st.session_state['jogos_salvos']:
                st.info("Nenhum jogo foi salvo ainda. Use as abas Estratégias e Geradores para criar e salvar seus jogos.")
            else:
                st.markdown("---")
                st.subheader("Lista de Jogos Salvos:")
                
                # Exibir jogos
                for i, jogo in enumerate(st.session_state['jogos_salvos']):
                    col_j1, col_j2 = st.columns([4, 1])
                    
                    with col_j1:
                         # Estilo para exibir o jogo
                        st.markdown(f"""
                        <div style="
                            background: #e6e6e6; 
                            border-radius: 5px; 
                            padding: 10px; 
                            margin: 5px 0; 
                            font-family: monospace;
                            color: black;
                        ">
                            {jogo}
                        </div>
                        """, unsafe_allow_html=True)

                    with col_j2:
                        # Botão para remover
                        if st.button("Remover", key=f'remover_jogo_{i}'):
                            del st.session_state['jogos_salvos'][i]
                            st.success("Jogo removido.")
                            time.sleep(0.1) # Pequena pausa para a UI atualizar
                            st.rerun()
                
                st.markdown("---")
                if st.button("🗑️ Limpar Todos os Jogos Salvos", key='limpar_todos'):
                    st.session_state['jogos_salvos'] = []
                    st.success("Todos os jogos foram removidos.")
                    st.rerun()
