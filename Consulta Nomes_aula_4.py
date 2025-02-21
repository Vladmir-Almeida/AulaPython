import dash
from dash import dcc, html
import requests
import pandas as pd
import plotly.express as px

app = dash.Dash(__name__)

def consultar_nomes():
    url = "https://servicodados.ibge.gov.br/api/v2/censos/nomes/joao|maria"

    response = requests.get(url)
    dados = response.json()
    nomes = []
    for nome_data in dados:
        nome = nome_data['nome']
        for res in nome_data['res']:
            periodo = res['periodo']
            frequencia = res['frequencia']
            nomes.append({'Nome': nome, 'Período': periodo, 'Frequência': frequencia})
    df = pd.DataFrame(nomes)
    return df
def criar_grafico(df):
    fig = px.line(df, x='Período', y='Frequencia', color='Nome', 
                  title='Frequencia dos nomes ao longo dos Períodos', 
                  labels={'Período': 'Período', 'Frequência': 'Frequência'})
    return fig
app.layout = html.Div([
    html.H1("Frequência de nomes ao longo dos Períodos"),
    dcc.Graph(id='grafico', figure=criar_grafico(consultar_nomes))
])   

if __name__ == "__main__":
    app.run_server(debug=True)