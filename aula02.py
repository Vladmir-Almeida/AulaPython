import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

#icionário com as informações da caixa do dropdown
dados_conceitos ={ 
    'java' : {'variaveis': 8, 'condicionais':10, 'loops':4, 'poo':3, 'funçoes':4},
    'python' : {'variaveis': 9, 'condicionais':7, 'loops':8, 'poo':4, 'funçoes':5},
    'sql' : {'variaveis': 7, 'condicionais':10, 'loops':9, 'poo':8, 'funçoes':4},
    'golang' : {'variaveis': 10, 'condicionais':5, 'loops':8, 'poo':4, 'funçoes':3},
    'javascript' : {'variaveis': 9, 'condicionais':7,'loops':5, 'poo':6, 'funçoes':8}
}

cores_map=dict(
    java='red',
    python='green',
    sql='yellow',
    golang='blue',
    javascript='pink')

app = dash.Dash(__name__)

app.layout = html.Div([
        html.H4('Sebrae Maranhão', style={'textAlign' : 'center'}), 
            html.Div(
                dcc.Dropdown(
                    id='dropdown_linguagens', 
                    options=[
                        {'label': 'Java', 'value': 'java'},
                        {'label': 'Python', 'value': 'python'},
                        {'label': 'SQL', 'value': 'sql'},
                        {'label': 'Golang', 'value': 'golang'},
                        {'label': 'JavaScript', 'value': 'javascript'}],
                    value=['java'],
                    multi=True,
                    style={'width': '50%', 'margin': '0 auto'}
                )
            ),
            dcc.Graph(id='grafico_linguagem')
    ], style={'width':'80%', 'margin':'0 auto'})

#uma função que vai ser chamada através de um evento
@app.callback(
    Output('grafico_linguagem', 'figure'),
    [Input('dropdown_linguagens', 'value')]
    )
def scarter_linguagens(linguagens_selecionadas):
    scarter_trace=[]

    for linguagem in linguagens_selecionadas:dados_linguagem = dados_conceitos[linguagem]
        for conceito, conhecimento in dados_linguagem.items():
            scarter_trace.append(
                go.Scatter(
                    x = [conceito],
                    y = [conhecimento],
                    mode='markers',
                    name=linguagem.title(),
                    marker={'size':15 , 'color': cores_map[linguagem]},
                    showlegend=False
                )
            )
    scartter_layout = go.layout(
        title="Meus conhecimentos em Linguagens",
        xaxis=dict(title='Conceitos', showgrid=False),
        yaxis=dict(title='Nivel de Conhecimento', showgrid=False)
    )
    return{'data':scarter_trace, 'layout':scartter_layout}
if __name__ == '__main__':
    app.run_server(debug=True)
