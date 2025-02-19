import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import dash 
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeSwitchAIO
from dash.dependencies import Input, Output
from dash import html, dcc, Input, Output
import os
os.chdir(os.path.dirname(__file__))
#configurando cores para os temas
dark_theme = 'darkly'
vapor_theme = 'vapor'
url_dark_theme = dbc.themes.DARKLY
url_vapor_theme = dbc.themes.VAPOR

#-------------------Dados---------------------------
# Importando os dados da tabela em csv
df = pd.read_csv('dataset_comp.csv')
df['dt_Venda'] = pd.to_datetime(df['dt_Venda'])
df['Mes'] = df['dt_Venda'].dt.strftime('%b').str.upper()

#--------------Listas----------------------------
# criar lista de clientes
lista_clientes = []
for cliente in df['Cliente'].unique():
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
    Output('output_cliente', 'children'),
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
def visual01(clientes, mes, categoria, taggle):
    template = dark_theme if taggle else vapor_theme

    nome_cliente = filtro_cliente(cliente)
    nome_categoria = filtro_categoria(categoria)
    nome_mes = filtro_mes(mes)

    cliente_mes_categoria = nome_cliente & nome_categoria & nome_mes 
    df_filtrado = df.loc[cliente_mes_categoria]

    df_grupo = df_filtrado.groupby(['Produto', 'Categorias'])['Total Vendas'].sum().reset_index()
    df_top5 = df_grupo.sort_values(by='Total Vendas', ascending=False).head(5)

    #Criando o Gráfico
    fig = px.bar(
        df_top5,
        x='Produto',
        y='Total Vendas',
        color='Total Vendas',
        text='Total Vendas',
        color_continuous_scale='blues',
        height=280,
        template=template
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(
       margin=dict(t=0),
       xaxis=dict(showgrid=False),
       yaxis=dict(showgrid=False, range=[
        df_top5['Total Vendas'].min() * 0,
        df_top5['Total Vendas'].max() * 1.2
        ]),
        xaxis_title = None,
        yaxis_title = None,
        xaxis_tickangle = -15,
        font=dict(size=15),
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)'
   )
    return fig

@app.callback(
    [
        Output('visual02', 'figure'),
        Output('visual03', 'figure')
    ],
    [
        Input('radio_mes', 'value'),
        Input('radio_categorias', 'value'),
        Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
    ]
)
def visual02_03(mes, categoria, taggle):
    #definido o tema que foi escolhido
    template = vapor_theme if taggle else dark_theme

    #filtrando apenas poe mês
    nome_mes = filtro_mes(mes)
    nome_categoria = filtro_categoria(categoria)

    #Combinar filtros
    mes_categoria = nome_mes & nome_categoria
    
    # filtrando o dataframe
    df2 = df.loc[nome_categoria]
    df3 = df.loc[mes_categoria]

    #gerar analise de dados
    df_vendasMesLoja2 = df2.groupby(['Mes', 'Loja', ])['Total Vendas'].sum().reset_index()
    df_vendasMesLoja3 = df3.groupby(['Mes', 'Loja', ])['Total Vendas'].sum().reset_index()

    #normaliza o tamanho das bolhas
    max_size = df_vendasMesLoja2['Total Vendas'].max()
    min_size = df_vendasMesLoja2['Total Vendas'].min()

    # definindo a ordem dos meses
    ordem_mes = [
        'JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
        'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'
    ]

    # DEFINIR AS CORES PARA CADA LOJA
    cores_lojas = {
        'Rio de Janeiro'    : 'green',
        'Salvador'          : 'yellow',
        'Santos'            : 'purple',
        'São Paulo'         : 'gray',
        'Três Rios'         : 'blue'            
    }

# criar o grafico do visual 02
    fig2 = go.Figure()
    for loja in df_vendasMesLoja2['Loja'].unique():
        df_loja = df_vendasMesLoja2[df_vendasMesLoja2['Loja'] == loja]
        cor = cores_lojas.get(loja, 'black')

        fig2.add_trace(
            go.Scatter(
                x = df_loja['Mes'],
                y = df_loja['Total Vendas'],
                mode= 'markers',
                marker= dict(
                    color = cor,
                    size = (df_loja['Total Vendas'] - min_size) / (max_size - min_size) * 50,
                    opacity=0.5,
                    line=dict(color=cor, width=0)       
                ),
                name=str(loja)
            )
        )
    fig2.update_layout(
        margin=dict(t=0),
        template=template,
        plot_bgcolor = 'rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        xaxis=dict(
            categoryorder='array',
            categoryarray=ordem_mes,
            showgrid=False
        ),
        yaxis=dict(showgrid=False)
    )
    fig3 = go.Figure(data=go.Scatterpolar(
        r = df_vendasMesLoja3['Total Vendas'],
        theta= df_vendasMesLoja3['Loja'],
        fill='toself',
        line=dict(color='rgb(31, 119, 180)', size=8),
        marker=dict(color='rgb(31, 119, 180)', size=8),
        opacity=0.7
    ))
    fig3.update_layout(
        template=template,
        polar=dict(
            radialaxis=dict(
                visible=True,
                tickfont=dict(size=10),
                tickangle=0,
                tickcolor='rgba(68,68,68,0)',
                ticklen= 5,
                tickwidth=1,
                tickprefix='',
                ticksuffix='',
                range=[0, max(df_vendasMesLoja3['Total Vendas']) + 1000]
            )
        ),
        font=dict(family='Fira Code', size=12),
        plot_bgcolor= 'rgba(0,0,0,0)',
        paper_bgcolor= 'rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)

    )
    return fig2, fig3


# Suindo servidor
if __name__ == '__main__':
    app.run_server(debug=True)
