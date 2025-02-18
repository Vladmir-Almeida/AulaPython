import plotly.graph_objs as graph_ob
import plotly.express as px
import pandas as pd
import dash 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import Input, Output
from dash import html, dcc, Input, Output
#configurando cores para os temas
dark_theme = 'darkly'
vapor_theme = 'vapor'
url_dark_theme = dbc.themes.DARKLY
url_vapor_theme = dbc.themes.VAPOR

#-------------------Dados---------------------------
# Importando os dados da tabela em csv
df = pd.read_csv('dataset_comp.csv')
df['dt_Venda'] = pd.todatetime(df['dt_Venda'])
df['Mes'] = df['dt_Venda'].dt.strftime('%b').str.upper()

#--------------Listas----------------------------
# criar lista de clientes
lista_clientes = []
for cliente in df['cliente'].unique():
    lista_clientes.append({
        'label': cliente,
        'value': cliente
    })

lista_clientes.append({
    'label': 'Todos os Clientes',
    'Value': 'todos_clientes'
})

# Criando lista de meses
mese_br = dict(
    JAN = 'JAN',
    FEV = 'FEV',
    MAR = 'MAR',
    APR = 'ABR',
    MAY = 'MAI',
    JUN = 'JUN',
    JUL = 'JUL',
    AUG = 'AGO',
    SEP = 'SET',
    OCT = 'OUT',
    NOV = 'NOV',
    DEC = 'DEZ'
)
lista_meses = []
for mes in df['Mes'].unique():
    mes_pt = mese_br.get(mes, mes)

    lista_meses.append({
        'label': mes_pt,
        'value' : mes
    })

lista_meses.append({
    'label': 'Ano Completo',
    'value': 'ano_completo'
})

# Criando Lista de categorias
lista_categorias = []
for categoria in df['Categorias'].unique():
    lista_categorias.append({
        'label': categoria,
        'value': categoria
    })
lista_categorias.append({
    'label': 'Todas as Categorias',
    'value': 'todas_categorias'
})
#Inicio do server
app = dash.Dash(__name__)
server = app.server

#----------------------LAYOUT----------------------------
layout_titulo = html.Div([
    #---ELEMENTO DO SELECT
    html.Div(
            dcc.Dropdown(
                id='dropdown_cliente',
                options=lista_clientes,
                placeholder=lista_clientes[-1]['label'],
                style={
                    'background-color': 'transparent',
                    'border': 'none',
                    'color': 'black'
                }
            ), style = {'width':'25%'}
    ),
    html.Div(
        html.Legend(
            'Sebrae Maranhão',
            style={
                'font-size':'150%',
                'tex-align': 'center'
            }
        ), style={'width':'50%'}
    ),
    html.Div(
        ThemeSwitchAIO(
            aio_id='theme',
            themes=[
                url_dark_theme,
                url_vapor_theme
            ]
        ), style={'with':'25%'}
    )
], style={
    'text-align': 'center',
    'display': 'flex',
    'justify-content': 'space-around',
    'align-items': 'center',
    'font-family': 'Fira Code',
    'margin-top': '20px'
})
layout_linh01 = html.Div([
    html.Div([
        html.H4(id='output_cliente'),
        dcc.Graph(id='visual01')
    ],style={
        'width': '65%',
        'text-align' : 'center'}
    ),
    html.Div([
        dbc.Checklist(
            id='radio_mes',
            options=lista_meses,
            inline=True
        ),
        dbc.RadioItems(
            id='radio_categorias',
            options=lista_categorias,
            inline=True
        )
    ], style={
        'width': '30%',
        'display': 'flex',
        'flex-direction': 'column',
        'justify-content':' space-evenly'})
], style={
    'display': 'flex',
    'justify-content': 'space-around',
    'margin-top': '40px',
    'height': '300px'
})
layout_linh02 = html.Div([
    html.Div([
        html.H4('Vendas por Mês e Loja/Cidade'),
        dcc.Graph(id='visual02')
    ],style={
        'width': '60%',
        'text-align': 'center'
        }),
    html.Div(dcc.Graph(id='visual03'), style={'width': '35%'})
    ], style={
        'display': 'flex',
        'justify-content': 'space-around',
        'margin-top': '40px',
        'height': '150px'
    })
#carregar o layout
app.layout = html.Div([
    layout_titulo,
    layout_linh01,
    layout_linh02
])
    
#-----------------FUNÇÕES DE APOIO------------------
def filtro_cliente(Cliente_selecionado):
    if Cliente_selecionado is None:
        return pd.Series(True, index=df.index)
    return df['Cliente'] == Cliente_selecionado

def filtro_categoria(categoria_selecionada):
    if categoria_selecionada is None:
        return pd.Series(True, index=df.index)
    elif categoria_selecionada == 'todas_categorias':
        return pd.Series(True, index=df.index)
    return df['Categorias'] == categoria_selecionada

def filtro_mes(meses_selecionados):
    if not meses_selecionados:
        return pd.Series(True, index=df.index)
    elif 'ano_completo' in meses_selecionados:
        return pd.Series(True, index=df.index)
    else:
        return df['Mes'].isin(meses_selecionados)

#---------------------CALLBAKC--------------------------
@app.callback(
    Output('output-cliente', 'children'),
    [
        Input('dropdown_cliente', 'value'),
        Input('radio_categorias', 'value')
    ]
)
def atualizar_texto(cliente_selecionado, categoria_selecionada):
    if cliente_selecionado and categoria_selecionada:
        return f'TOP5 {categoria_selecionada} | Clientes: {cliente_selecionado}'
    
    elif cliente_selecionado:
        return f'TOP5 Produtos | Clientes: {cliente_selecionado}'
    
    elif categoria_selecionada:
        return f'TOP5 {categoria_selecionada}'
    
    return f'TOP5 Categoria'

@app.callback(
    Output('visual01', 'figure'),
    [
        Input('dropdown_cliente', 'value'),
        Input('radio_mes', 'value'),
        Input('radio_categorias', 'value'),
        Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
    ]
)