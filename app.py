import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas
from io import StringIO

app = dash.Dash()

csv = StringIO("""gene,cond1,cond2,cond3,cond4
gene1,0.2,0.7,0.2,0.7
gene2,0.4,0.8,0.2,0.8
gene3,0.5,0.8,0.1,0.9
gene4,0.6,0.8,0.3,0.8
""")
df = pandas.read_csv(csv, index_col=0)


app.layout = html.Div([
    dcc.Graph(
        id='scatter',
        figure={
            'data': [
                go.Scatter(
                    x=df['cond1'],
                    y=df['cond2'],
                    mode='markers'
                )
            ]
        }
    ),
    dcc.Graph(
        id='heatmap',
        figure={
            'data': [
                go.Heatmap(
                    z=df.as_matrix()
                )
            ]
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)