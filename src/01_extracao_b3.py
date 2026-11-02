import yfinance as yf
import pandas as pd
import os

# 1. Definir os ativos (sufixo .SA para mercado brasileiro) e o período obrigatório
ativos = ['WEGE3.SA', 'EMBR3.SA', 'VALE3.SA', 'GGBR4.SA', 'KLBN11.SA', 'PETR4.SA', 
          'PRIO3.SA', 'EGIE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'ABEV3.SA', 'RENT3.SA']

data_inicio = '2021-01-01'
data_fim = '2023-12-31' # yfinance exclui o último dia, então use '2024-01-01' na query se quiser garantir o dia 31

print("Iniciando o download dos dados da B3...")
df_b3 = yf.download(ativos, start=data_inicio, end='2024-01-01')

# 2. Formatar o DataFrame (empilhar os ativos para facilitar a análise)
df_b3 = df_b3.stack(level=1, future_stack=True).rename_axis(['Data', 'Ativo']).reset_index()

# Garantir que as colunas obrigatórias estão presentes e arredondar valores
colunas_desejadas = ['Data', 'Ativo', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
df_b3 = df_b3[colunas_desejadas]
df_b3.iloc[:, 2:] = df_b3.iloc[:, 2:].round(2)

# 3. Salvar usando caminho relativo (Exigência 4.3 da documentação)
caminho_saida = os.path.join('..', 'data', 'cotacoes_b3_2021_2023.csv') 
# Nota: se estiver rodando um arquivo .py na raiz, mude para os.path.join('data', '...')

df_b3.to_csv(caminho_saida, index=False)
print(f"Extração concluída! Arquivo salvo em: {caminho_saida}")