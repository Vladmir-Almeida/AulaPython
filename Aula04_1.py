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
        df_produto = df_produto.groupby(['produto'])['valor'].sum().reset_index().sort_values(by='valor', ascending=False)
        fig = px.bar(
            df_produto,
            x='produto',
            y='valor',
            title='Vendas por Produto',
            color= 'valor')

        return fig
    
    #grafico de pizza para vendas por região
    def analise_vendas_por_regiao(self, regioes_filtradas):
        df_regiao = self.dados[self.dados['regiao'].isin(regioes_filtradas)]
        df_regiao = df_regiao.groupby('regiao')['valor'].sum().reset_index().sort_values(by='valor', ascending=False)
        fig = px.pie(
            df_regiao,
            names = 'regiao',
            values = 'valor',
            title = 'Vendas por Região',
            color = 'valor'
        )
        return fig
    def analise_vendas_mensais(self, ano_filtrado):
        df_mes = self.dados[self.dados['ano'] == ano_filtrado]
        df_mes = df_mes.groupby(['ano', 'mes'])['valor'].sum().reset_index()
        fig = px.line(
            df_mes,
            x = 'mes',
            y = 'valor',
            color = 'ano',
            title = f'Vendas Mensais - {ano_filtrado}',
            markers = True,
            line_shape = 'spline'
        )
        return fig
    # grafico de vendas diarias ao longo do tempo
    def analise_vendas_diarias(self, data_inicio, data_fim):
        df_dia = self.dados[(self.dados['data'] >= data_inicio) & (self.dados['data'] <= data_fim)]
        df_dia = df_dia.groupby('data')['valor'].sum().reset_index()
        fig = px.line(
            df_dia,
            x = 'data',
            y = 'valor',
            title = 'Vendas Diarias',
            markers = True
        )
        return fig
    # grafico de vendas por semana (analisa o impacto diario)
    def analise_vendas_por_dia_da_semana(self):
        df_dia_semana = self.dados.groupby('dia_da_semana')['valor'].sum().reset_index()
        df_dia_semana['dia_da_semana'] = df_dia_semana['dia_da_semana'].map({
            0:'Segunda',
            1:'Terça',
            2:'Quarta',
            3:'Quinta',
            4:'Sexta',
            5:'Sábado',
            6:'Domingo'
        })
        fig = px.bar(
            df_dia_semana,
            x = 'dia_da_semana',
            y = 'valor',
            title = 'vendas por dia da Semana',
            color = 'valor'
        )
        return fig
# identifica os outliers com base em umintervalo interquartil
    def analise_outliers(self):
        q1 = self.dados['valor'].quantile(0.25)
        q3 = self.dados['valor'].quantile(0.75)
        iqr = q3 - q1
        lim_inferior = q1 - 1.5 * iqr
        lim_superior = q3 + 1.5 * iqr
        outliers = self.dados[(self.dados['valor'] <= lim_inferior) | (self.dados['valor'] >= lim_superior) ]
        fig = px.scatter(
            outliers,
            x = 'data',
            y = 'valor',
            title = 'Outliers de Vendas'
        )
        return fig
#retona o grafico de distribuição de vendas usando o plotly
    
    def distribuicao_vendas(self):
        fig = px.histogram(
            self.dados,
            x = 'valor',
            title = 'Distribuição de vendas',
            nbins = 30
        )
        return fig
    # calculos de média e desvio padrão das vendas
    def analise_media_desvio(self):
        media = self.dados['valor'].mean()
        desvio = self.dados['valor'].std()
        return media, desvio
    # def vendas acumuladas ao longo do tempo com insight poderosos
    
    def vendas_acumuladas(self):
        df_acumulado = self.dados.groupby('data')['valor'].sum().cumsum().reset_index()
        #calculos adicionais para enriquecer a nossa analise
        df_acumulado['media_movel_7'] = df_acumulado['valor'].rolling(window=7).mean()
        #media movel de 7 dias
        df_acumulado['desvio_padrao_7'] = df_acumulado['valor'].rolling(window=7).std()
        #desvio padrão
        df_acumulado['crescimento_percentual'] = df_acumulado['valor'].pct_change() * 100
        #calcula a variação percentual entre o valor atual e o valor anterioir (do dia anterior)
        df_acumulado['max_valor'] = df_acumulado['valor'].expanding().max()
        # valor maximo acumulado
        df_acumulado['min_valor'] = df_acumulado['valor'].expanding().min()
         # valor minimo acumulado

         # criando gráfico
        fig = px.line(
            df_acumulado,
            x = 'data',
            y = ['valor', 'media_movel_7', 'max_valor', 'min_valor'],
            title = 'Vendas Acumuladas ao Longo do tempo com Inghts Estatisticos',
            labels = {'valor':'Vendas Acumuladas', 'media_movel_7': 'Media movel (7 dias)','max_valor':'Máximo acumulado', 'min_valor': 'Minimo acumulado'},
            markers = True

         )
	# adicionando  o crescimento percentual ao grafico como um LINHA DE ANOTAÇÕES
        fig.add_trace(
            go.Scatter(
                x = df_acumulado['data'],
                y = df_acumulado['crescimento_percentual'],
                mode = 'lines+markers',
                name = 'Crescimento Percentual',
                line = dict(color='orange', width=2, dash='dot'),
                yaxis = 'y2'
            )
        )
	#estilização do grafico, ajustando a estética e com serão mostrados os valores
        fig.update_layout(
            title_font = dict(size=20, family='Poppins', color='#2980b9'),
            plot_bgcolor = "#34495e",
            paper_bgcolor = "#2c3e50",
            font = dict(color='#ecf0f1', family='Roboto'),
            xaxis = dict(
                title = 'Data',
                tickformat = '%Y-%m-%d',
                showgrid = True,
                gridcolor = '#7f8c8d',
                tickangle = 45
            ),
            yaxis = dict(
                title = 'Vendas Acumuladas',
                showgrid = True,
                gridcolor = '#7f8c8d'
            ),
            yaxis2 = dict(
                title = 'Crescimento Percentual (%)',
                showgrid = False,
                side = 'right',
                overlaying = 'y',
                tickformat = '.1f'
            ),
            legend = dict(
                title = 'Métricas',
                orientation = 'h',
                yanchor = 'bottom',
                y = 1.1,
                xanchor = 'center',
                x = 0.5
            ),
            hovermode = "x unified",
            autosize= True,
            margin = dict(t=50, b=50, l=40, r=40),
            shapes= [
                dict(
                    type = "line",
                    x0=df_acumulado['data'].min(),
                    x1=df_acumulado['data'].max(),
                    y0=df_acumulado['max_valor'].max(),
                    y1=df_acumulado['max_valor']. max(),
                    line=dict(color="red", width=2, dash='dash'),
                    name="Máximo Histórico"
                ),
                dict(
                    type = "line",
                    x0=df_acumulado['data'].min(),
                    x1=df_acumulado['data'].max(),
                    y0=df_acumulado['max_valor'].max(),
                    y1=df_acumulado['max_valor']. max(),
                    line=dict(color="green", width=2, dash='dash'),
                    name="Minimo Histórico"
                )
            ]
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
        dcc.Graph(id='grafico-regiao'),
        dcc.Graph(id='grafico-mensal'),
        dcc.Graph(id='grafico-diario'),
        dcc.Graph(id='grafico-dia-da-semana'),
        dcc.Graph(id='grafico-outliers'),
        dcc.Graph(id='grafico-distribuicao'),
        dcc.Graph(id='grafico-media-desvio'),
        dcc.Graph(id='grafico-acumulado')
    ])
])

#------------------------Callbacks
@app.callback(
    Output('grafico-produto', 'figure'),
    Output('grafico-regiao', 'figure'),
    Output('grafico-mensal', 'figure'),
    Output('grafico-diario', 'figure'),
    Output('grafico-dia-da-semana', 'figure'),
    Output('grafico-outliers', 'figure'),
    Output('grafico-distribuicao', 'figure'),
    Output('grafico-media-desvio', 'figure'),
    Output('grafico-acumulado', 'figure'),
    Input('produto-dropdown', 'value'),
    Input('regiao-dropdown', 'value'),
    Input('ano-dropdown', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)

def upgrade_graphs(produtos, regioes, ano, start_date, end_date):
    try:
        # converte a data para o formatp correto
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        #atualizar os graficos de acordo com os filtros selecionados
        fig_regiao = analise.analise_vendas_por_regiao(regioes)
        fig_produto = analise.analise_vendas_por_produto(produtos)
        fig_mensal = analise.analise_vendas_mensais(ano)
        fig_diario = analise.analise_vendas_diarias(start_date, end_date)
        fig_dia_da_semana = analise.analise_vendas_por_dia_da_semana()
        fig_outliers = analise.analise_outliers()
        fig_distribuicao = analise.distribuicao_vendas()
        media, desvio = analise.analise_media_desvio()
        fig_media_desvio = go.Figure(data=[
            go.Bar(
                x = ['Média', 'Desvio Padrão'],
                y = [media, desvio],
                marker_color = ['blue','red'],
            )
        ], layout= go.Layout(title=f'Media e Desvio padrao: Média={media:.2f} Desvio={desvio:.2f}'))

        fig_acumulado = analise.vendas_acumuladas()
        
        return fig_produto, fig_regiao, fig_mensal, fig_diario, fig_dia_da_semana, fig_outliers, fig_distribuicao, fig_media_desvio, fig_acumulado
        
    except Exception as e:
        # sempre que ocorrer algum erro, mostrar a mensagem de erro e retornar gráficos vazios
        print(f'Erro ao atualizar os gráficos: {str(e)}')
        return [go.Figure()] * 9 # por enquanto tem 9
#  roda o app
if __name__ == '__main__':
    app.run_server(debug=True)
 
