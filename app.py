import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import base64

# ==========================================
# 1. CONFIGURAÇÃO E CSS
# ==========================================
st.set_page_config(page_title="Terminal Analytics B3", page_icon="📈", layout="wide")

BG_COLOR = '#131722'       
SIDEBAR_COLOR = '#001B74'  
GRID_COLOR = '#2a2e39'
TEXT_COLOR = '#d1d4dc'
CYAN_B3 = '#00E5FF'


LOGO_B3_B64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgNDAiPjx0ZXh0IHg9IjAiIHk9IjMwIiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iMzAiIGZvbnQtd2VpZ2h0PSJib2xkIiBmaWxsPSIjZmZmZmZmIj5bQl08dHNwYW4gZHk9Ii0xNCIgZm9udC1zaXplPSIyMCI+MzwvdHNwYW4+PC90ZXh0Pjwvc3ZnPg=="

st.markdown(f"""
    <style>
    /* Fundo da tela principal */
    .stApp {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; }}
    
    /* Fundo da barra lateral (Menu B3) */
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_COLOR}; }}
    
    h1, h2, h3, h4 {{ color: #ffffff; font-family: 'Segoe UI', sans-serif; }}
    div[data-testid="metric-container"] {{
        background-color: {BG_COLOR}; border-left: 4px solid #089981; padding: 15px; border-radius: 5px; border: 1px solid {GRID_COLOR};
    }}
    .asset-card {{ background-color: transparent; padding: 8px 0; margin-bottom: 5px; display: flex; align-items: center; border-bottom: 1px solid {GRID_COLOR}; }}
    .asset-logo {{ width: 38px; height: 38px; border-radius: 50%; margin-right: 12px; object-fit: cover; background-color: transparent; border: none; }}
    .asset-info {{ flex-grow: 1; display: flex; flex-direction: column; }}
    .asset-name {{ font-weight: bold; color: {TEXT_COLOR}; font-size: 1.05rem; }}
    .asset-subname {{ color: #787b86; font-size: 0.8rem; margin-top: 2px; }}
    .asset-price-container {{ text-align: right; display: flex; flex-direction: column; }}
    .asset-price {{ color: {TEXT_COLOR}; font-size: 1.05rem; }}
    .asset-var {{ font-size: 0.85rem; margin-top: 2px; }}
    header {{ visibility: hidden; }}
    </style>
""", unsafe_allow_html=True)

def aplicar_estilo_terminal(fig, height=500):
    fig.update_layout(
        plot_bgcolor=BG_COLOR, paper_bgcolor=BG_COLOR, font=dict(color=TEXT_COLOR),
        margin=dict(l=10, r=10, t=40, b=10), height=height,
        xaxis=dict(showgrid=False, zeroline=False, color=TEXT_COLOR),
        yaxis=dict(showgrid=True, gridcolor=GRID_COLOR, gridwidth=1, zeroline=False, color=TEXT_COLOR),
        hovermode="x unified"
    )
    return fig

# ==========================================
# 2. MOTOR VETORIAL DE LOGOS 
# ==========================================
nomes_empresas = {
    'WEGE3.SA': 'WEG S.A.', 'BBAS3.SA': 'Banco do Brasil S.A.', 'VALE3.SA': 'Vale S.A.', 
    'GGBR4.SA': 'Gerdau S.A.', 'KLBN11.SA': 'Klabin S.A.', 'PETR4.SA': 'Petroleo Brasileiro SA Pfd', 
    'PRIO3.SA': 'Petro Rio S.A.', 'EGIE3.SA': 'Engie Brasil Energia S.A.', 'ITUB4.SA': 'Itau Unibanco Holding SA', 
    'BBDC4.SA': 'Banco Bradesco SA Pfd', 'ABEV3.SA': 'Ambev S.A.', 'RENT3.SA': 'Localiza Rent a Car S.A.'
}

def get_logo_svg(ativo):
    cores_oficiais = {
        'WEGE3.SA': ('#00579D', '#FFFFFF', 'WEG'), 'BBAS3.SA': ('#F9D308', '#0038A8', 'bb'),
        'VALE3.SA': ('#007A53', '#FFBA00', 'VALE'), 'GGBR4.SA': ('#003087', '#FFFFFF', 'Gerdau'),
        'KLBN11.SA': ('#005E38', '#FFFFFF', 'Klabin'), 'PETR4.SA': ('#008542', '#F9D308', 'BR'),
        'PRIO3.SA': ('#000000', '#FFFFFF', 'PRIO'), 'EGIE3.SA': ('#00A3E0', '#FFFFFF', 'ENGIE'),
        'ITUB4.SA': ('#EC7000', '#003A70', 'itaú'), 'BBDC4.SA': ('#CC092F', '#FFFFFF', 'Bradesco'),
        'ABEV3.SA': ('#FABB00', '#000000', 'ambev'), 'RENT3.SA': ('#009639', '#FFFFFF', 'Localiza')
    }
    bg, fg, texto = cores_oficiais.get(ativo, ('#2a2e39', '#ffffff', ativo[:4]))
    tamanho_fonte = 42 if len(texto) <= 2 else (28 if len(texto) <= 4 else 18)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="50" fill="{bg}"/><text x="50" y="50" font-family="Arial, Helvetica, sans-serif" font-size="{tamanho_fonte}" font-weight="bold" fill="{fg}" text-anchor="middle" dominant-baseline="central">{texto}</text></svg>"""
    return f"data:image/svg+xml;base64,{base64.b64encode(svg.encode('utf-8')).decode('utf-8')}"

# ==========================================
# 3. INGESTÃO DE DADOS
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    try:
        conn = st.connection("postgresql", type="sql")
        df = conn.query("SELECT * FROM cotacoes_b3_2021_2023;")
        df['Data'] = pd.to_datetime(df['Data'])
        return df
    except Exception as e:
        try:
            df = pd.read_csv(os.path.join("data", "cotacoes_b3_2021_2023.csv"))
            df['Data'] = pd.to_datetime(df['Data'])
            return df
        except:
            return pd.DataFrame()

df = load_data()

if 'reset_key' not in st.session_state:
    st.session_state.reset_key = False

def resetar_filtros():
    st.session_state.reset_key = not st.session_state.reset_key

if not df.empty:
    df_sorted = df.sort_values(by=['Ativo', 'Data'])
    conteudo_ticker = ""
    for ativo in df_sorted['Ativo'].unique():
        df_ativo = df_sorted[df_sorted['Ativo'] == ativo]
        if len(df_ativo) >= 2:
            ultimo, anterior = df_ativo['Adj Close'].iloc[-1], df_ativo['Adj Close'].iloc[-2]
            var = ((ultimo - anterior) / anterior) * 100
            cor, seta = ("ticker-up", "▲") if var >= 0 else ("ticker-down", "▼")
            conteudo_ticker += f"<div class='ticker-item'><img src='{get_logo_svg(ativo)}' class='ticker-logo'><span style='color:#d1d4dc'>{ativo[:5]}</span><span style='color:#d1d4dc; margin: 0 5px;'>R$ {ultimo:.2f}</span><span class='{cor}'>{seta} {var:+.2f}%</span></div>"
            
    ticker_html = f"<div class='ticker-wrap'><div class='ticker'>{conteudo_ticker}{conteudo_ticker}</div></div>"
    components.html(f"""
        <style>
            body {{ margin: 0; background-color: {BG_COLOR}; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
            .ticker-wrap {{ width: 100%; overflow: hidden; background-color: {BG_COLOR}; padding: 8px 0; display: flex; white-space: nowrap; }}
            .ticker {{ display: flex; flex-shrink: 0; animation: ticker 40s linear infinite; }}
            @keyframes ticker {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
            .ticker-item {{ display: inline-flex; align-items: center; padding: 0 1.5rem; font-size: 1.05rem; font-weight: bold; flex-shrink: 0; }}
            .ticker-logo {{ width: 24px; height: 24px; border-radius: 50%; margin-right: 8px; object-fit: cover; background-color: transparent; border: none; }}
            .ticker-up {{ color: #089981; }} .ticker-down {{ color: #f23645; }}
        </style>
        {ticker_html}
    """, height=45)

    with st.sidebar:
        st.markdown(f"""<div style="display: flex; justify-content: center; margin-bottom: 20px;"><img src="{LOGO_B3_B64}" width="100"></div>""", unsafe_allow_html=True)
        st.button("🔄 Resetar Painel", on_click=resetar_filtros, use_container_width=True)
        st.markdown("---")
        ativos_unicos = df['Ativo'].unique().tolist()
        ativos_selecionados = st.multiselect("Portfólio de Ativos", options=ativos_unicos, default=ativos_unicos, key=f"ativos_{st.session_state.reset_key}")
        data_min, data_max = df['Data'].min().date(), df['Data'].max().date()
        datas_selecionadas = st.date_input("Janela Temporal", value=(data_min, data_max), min_value=data_min, max_value=data_max, key=f"datas_{st.session_state.reset_key}")

    if len(datas_selecionadas) == 2:
        df_filtrado = df_sorted[(df_sorted['Ativo'].isin(ativos_selecionados)) & (df_sorted['Data'].dt.date >= datas_selecionadas[0]) & (df_sorted['Data'].dt.date <= datas_selecionadas[1])].copy()
    else:
        df_filtrado = pd.DataFrame()

    if not df_filtrado.empty:
        st.sidebar.download_button("📥 Exportar Dados", data=df_filtrado.to_csv(index=False).encode('utf-8'), file_name="relatorio_b3.csv", mime="text/csv", use_container_width=True)

        st.markdown(f"""
            <div style='display: flex; align-items: center; margin-top: -20px; margin-bottom: 20px;'>
                <img src='{LOGO_B3_B64}' width='60' style='margin-right: 15px;'>
                <h2 style='margin: 0;'>Terminal Bloomberg - Advanced Analytics</h2>
            </div>
        """, unsafe_allow_html=True)
        
        df_filtrado['Retorno_Diario'] = df_filtrado.groupby('Ativo')['Adj Close'].pct_change()
        df_filtrado['Base_100'] = df_filtrado.groupby('Ativo')['Adj Close'].transform(lambda x: (x / x.iloc[0]) * 100)
        
        retornos_acumulados = df_filtrado.groupby('Ativo')['Base_100'].last() - 100
        volatilidade_anualizada = df_filtrado.groupby('Ativo')['Retorno_Diario'].std() * (252 ** 0.5) * 100
        retorno_anualizado = df_filtrado.groupby('Ativo')['Retorno_Diario'].mean() * 252 * 100
        
        taxa_livre_risco = 10.0 
        sharpe_ratio = (retorno_anualizado - taxa_livre_risco) / volatilidade_anualizada
        ativo_maior_sharpe = sharpe_ratio.idxmax()

        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("Retorno Médio Carteira", f"{retornos_acumulados.mean():.2f}%")
        kpi2.metric("Ativo Destaque (Retorno)", retornos_acumulados.idxmax(), f"{retornos_acumulados.max():.2f}%")
        kpi3.metric("Pior Performance", retornos_acumulados.idxmin(), f"{retornos_acumulados.min():.2f}%")
        kpi4.metric("Risco Médio (Vol)", f"{volatilidade_anualizada.mean():.2f}% a.a.")
        kpi5.metric("Maior Índice Sharpe", ativo_maior_sharpe, f"{sharpe_ratio.max():.2f}")
        st.markdown("---")

        aba1, aba2, aba3, aba4, aba5 = st.tabs(["📈 Rentabilidade", "⚠️ Risco vs Retorno", "🔗 Correlação Setorial", "🕯️ Análise Técnica", "📋 Auditoria"])

        with aba1:
            col_grafico, col_lista = st.columns([3, 1])
            with col_grafico:
                st.subheader("Evolução Normalizada (Base 100)")
                ordem_legenda = retornos_acumulados.sort_values(ascending=False).index.tolist()
                cores_vibrantes = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
                
                fig_base100 = px.line(df_filtrado, x='Data', y='Base_100', color='Ativo', 
                                      category_orders={'Ativo': ordem_legenda}, color_discrete_sequence=cores_vibrantes)
                fig_base100.add_hline(y=100, line_dash="dash", line_color="#089981")
                fig_base100 = aplicar_estilo_terminal(fig_base100)
                
                fig_base100.update_traces(hovertemplate="%{y:.2f}") 
                st.plotly_chart(fig_base100, use_container_width=True)

            with col_lista:
                st.subheader("Cotações")
                for ativo in ordem_legenda:
                    df_ativo_filt = df_filtrado[df_filtrado['Ativo'] == ativo]
                    if not df_ativo_filt.empty:
                        preco, preco_ant = df_ativo_filt['Adj Close'].iloc[-1], df_ativo_filt['Adj Close'].iloc[0]
                        var_periodo = ((preco - preco_ant) / preco_ant) * 100
                        cor = "#089981" if var_periodo >= 0 else "#f23645"
                        st.markdown(f"""
                        <div class="asset-card">
                            <img src="{get_logo_svg(ativo)}" class="asset-logo">
                            <div class="asset-info"><div class="asset-name">{ativo[:5]} <span style="color:#d1d4dc; font-size: 0.7rem;">D</span></div><div class="asset-subname">{nomes_empresas.get(ativo, "B3 S.A.")}</div></div>
                            <div class="asset-price-container"><div class="asset-price">{preco:.2f}</div><div class="asset-var" style="color: {cor};">{var_periodo:+.2f}%</div></div>
                        </div>""", unsafe_allow_html=True)

        with aba2:
            st.subheader("Matriz de Risco e Drawdown")
            col1, col2 = st.columns(2)
            with col1:
                df_risco = pd.DataFrame({'Retorno': retornos_acumulados, 'Volatilidade': volatilidade_anualizada}).reset_index()
                df_risco = pd.merge(df_risco, df_filtrado.groupby('Ativo')['Volume'].mean().reset_index(), on='Ativo')
                fig_dispersao = px.scatter(df_risco, x='Volatilidade', y='Retorno', color='Ativo', size='Volume', 
                                           title="Dispersão: Volatilidade vs Retorno", color_discrete_sequence=cores_vibrantes)
                fig_dispersao.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
                fig_dispersao = aplicar_estilo_terminal(fig_dispersao, height=450)
                
                fig_dispersao.update_traces(hovertemplate="Volatilidade: %{x:.2f}%<br>Retorno: %{y:.2f}%")
                st.plotly_chart(fig_dispersao, use_container_width=True)
            with col2:
                df_filtrado['Pico'] = df_filtrado.groupby('Ativo')['Adj Close'].cummax()
                df_filtrado['Drawdown'] = ((df_filtrado['Adj Close'] - df_filtrado['Pico']) / df_filtrado['Pico']) * 100
                fig_drawdown = px.line(df_filtrado, x='Data', y='Drawdown', color='Ativo', 
                                       title="Drawdown Máximo", color_discrete_sequence=cores_vibrantes)
                fig_drawdown.update_traces(fill='tozeroy', line=dict(width=1), hovertemplate="%{y:.2f}%")
                fig_drawdown = aplicar_estilo_terminal(fig_drawdown, height=450)
                st.plotly_chart(fig_drawdown, use_container_width=True)

        with aba3:
            st.subheader("Correlação Setorial de Ativos")
            df_retornos_pivot = df_filtrado.pivot_table(index='Data', columns='Ativo', values='Retorno_Diario').dropna()
            matriz_corr = df_retornos_pivot.corr()
            fig_corr = px.imshow(matriz_corr, text_auto=".2f", color_continuous_scale='Teal_r', aspect="auto")
            fig_corr = aplicar_estilo_terminal(fig_corr, height=600)
            fig_corr.update_traces(hovertemplate="Correlação: %{z:.2f}")
            st.plotly_chart(fig_corr, use_container_width=True)

        with aba4:
            st.subheader("Análise Técnica Avançada")
            col3, col4 = st.columns([1, 2])
            with col4:
                ativo_mm = st.selectbox("Inspecionar Ativo (Candlestick + SMAs):", df_filtrado['Ativo'].unique())
                df_ativo_mm = df_filtrado[df_filtrado['Ativo'] == ativo_mm].copy()
                df_ativo_mm['SMA_21'] = df_ativo_mm['Close'].rolling(window=21).mean()
                df_ativo_mm['SMA_50'] = df_ativo_mm['Close'].rolling(window=50).mean()
                
                
                fig_candle = go.Figure(data=[go.Candlestick(
                    x=df_ativo_mm['Data'], open=df_ativo_mm['Open'], high=df_ativo_mm['High'], 
                    low=df_ativo_mm['Low'], close=df_ativo_mm['Close'], name='Preço',
                    increasing_line_color='#089981', decreasing_line_color='#f23645'
                )])
                fig_candle.add_trace(go.Scatter(x=df_ativo_mm['Data'], y=df_ativo_mm['SMA_21'], line=dict(color='#FABB00', width=1.5), name='SMA 21'))
                fig_candle.add_trace(go.Scatter(x=df_ativo_mm['Data'], y=df_ativo_mm['SMA_50'], line=dict(color=CYAN_B3, width=1.5), name='SMA 50'))
                
                fig_candle = aplicar_estilo_terminal(fig_candle, height=550)
                fig_candle.update_layout(xaxis_rangeslider_visible=False, title=f"Ação do Preço - {ativo_mm}")
                
                
                fig_candle.update_traces(selector=dict(name='SMA 21'), hovertemplate="SMA 21: %{y:.2f}")
                fig_candle.update_traces(selector=dict(name='SMA 50'), hovertemplate="SMA 50: %{y:.2f}")
                
                st.plotly_chart(fig_candle, use_container_width=True)

            with col3:
                st.markdown("<div style='height: 73px;'></div>", unsafe_allow_html=True)
                df_filtrado['Retorno_Perc'] = df_filtrado['Retorno_Diario'] * 100
                fig_hist = px.histogram(df_filtrado, x='Retorno_Perc', color='Ativo', 
                                        color_discrete_sequence=cores_vibrantes, title="Distribuição de Frequência")
                fig_hist = aplicar_estilo_terminal(fig_hist, height=477)
                fig_hist.update_layout(showlegend=False)
                
                fig_hist.update_traces(hovertemplate="Retorno: %{x:.2f}%<br>Ocorrências: %{y}")
                st.plotly_chart(fig_hist, use_container_width=True)



        with aba5:
            st.subheader("Log Auditável de Transações (Bruto)")
            st.dataframe(df_filtrado[['Data', 'Ativo', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Base_100']], use_container_width=True)