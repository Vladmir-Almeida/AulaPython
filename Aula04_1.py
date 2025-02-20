import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import base64

# Bloco especifico para carregar corretamente arquivos usando o visual code
import os
os.chdir(os.path.dirname(__file__))

# inializando o app dash
app = dash.Dash(__name__)
# carrega para o dataset os dados do vendas.csv
df = pd.read_csv('vendas.csv')
#cria a classe para a estrutura da analise de dadoss
class AnalisadorDeVendas:
    def __init__(self, dados):
        # inicializa a classe com o dataframe da tabela vendas
        self.dados = dados
        self.limpar_dados()

    def limpar_dados(self):
        # limpeza e preparação dos dados para análises com as demais funções
        self.dados['data'] = pd.to_datetime(self.dados['data'], errors='coerce') #converte as data em formato de texto para o formato datetime
        self.dados['valor'] = self.dados['valor'].replace({',':'.'}, regex=True).astype(float) # corrige os valores monetários, troca virgula por ponto
        self.dados.dropna(subset=['produto', 'valor'], inplace=True) # remove os dados ausente em clunas importantes
        self.dados['mes'] = self.dados['data'].dt.month #separa o mes da data e insere na coluna mes
        self.dados['ano'] = self.dados['data'].dt.year
        self.dados['dia'] = self.dados['data'].dt.day
        self.dados['dia_da_semana'] = self.dados['data'].dt.weekday # separa o dia da semana sendo 0 a segunda e 6 domingo
          
    def analise_vendas_por_produto(self, produtos_filtrados):
        """Retorna gráfico de vendas totais por produto."""
        df_produto = self.dados[self.dados['produto'].isin(produtos_filtrados)]
        df_produto = df_produto.groupby('produto')['valor'].sum().reset_index().sort_values(by='valor', ascending=False)
        fig = px.bar(
            df_produto,
            x='produto',
            y='valor',
            title='Vendas por Produto',
            color= "valor")

        return fig
    
    #grafico de pizza para vendas por região
    def analise_vendas_por_regiao(self, regioes_filtradas):
        df_regiao = self.dados[self.dados['regiao'].isin(regioes_filtradas)]
        df_regiao = df_regiao.groupby('regiao')['valor'].sum().reset_index().sort_values(by='valor', ascending=False)
        fig = px.pie(
            df_regiao,
            names = 'regiao',
            value = 'valor',
            title = 'Vendas por Região',
            color = 'valor'
        )
# --------------------------------instaciar o objeto de analise de vendas
analise = AnalisadorDeVendas(df)
# --------------------------------layout do app Dash
app.layout = html.Div([
    html.H1('Dashboards de analise de vendas', style={'text-align':'center'}),
    # criar filtros de seleção para o painel
    html.Div([
        html.Label('Selecione os Produtos'),
        dcc.Dropdown(
            id = 'produto-dropdown',
            options = [{'label':produto,'value': produto} for produto in df['produto'].unique()], 
            multi = True,
            value = df['produto'].unique().tolist(),
            style = {'width':'48%'}
        ),
        html.Label('Selecione as Regiões'),
        dcc.Dropdown(
            id = 'regiao-dropdown',
            options = [{'label':regiao,'value': regiao} for regiao in df['regiao'].unique()], 
            multi = True,
            value = df['regiao'].unique().tolist(),
            style = {'width':'48%'}
        ),
        html.Label('Selecione o Ano'),
        dcc.Dropdown(
            id = 'ano-dropdown',
            options = [{'label':str(ano),'value': ano} for ano in df['ano'].unique()], 
            value = df['ano'].min(),
            style = {'width':'48%'}
        ),
        html.Label('Selecione um Periodo'),
        dcc.DatePickerRange(
            id = 'date-picker-range',
            start_date = df['data'].min().date(), 
            end_date = df['data'].max().date(),
            display_format = 'YYYY-MM-DD',
            style = {'width':'48%'}
        ),
    ], style={'padding':'20px'}),
    # graficos
    html.Div([
        dcc.Graph(id='grafico-produto'),
        dcc.Graph(id='grafico-regiao')
    ])
])
#------------------------Callbacks
@app.callback(
    Output('grafico-produto', 'figure'),
    Output('grafico-regiao', 'figure'),
    Input('produto-dropdown', 'value'),
    Input('regiao-dropdown', 'value'),
    Input('ano-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)

def upgrade_graphs(produtos, regioes, ano, star_date, end_date):
    try:
        # converte a data para o formatp correto
        star_date = pd.to_datetime(star_date)
        end_date = pd.to_datetime(end_date)
        #atualizar os graficos de acordo com os filtros selecionados
        fig_produto = analise.analise_vendas_por_produto(produtos)
        return fig_produto
    except Exception as e:
        # sempre que ocorrer algum erro, mostrar a mensagem de erro e retornar gráficos vazios
        print(f'Erro ao atualizar os gráficos: {str(e)}')
        return go.Figure() 
#  roda o app
if __name__ == '__main__':
    app.run_server(debug=True)
