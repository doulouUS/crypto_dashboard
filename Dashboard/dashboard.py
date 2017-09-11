import plotly
import plotly.graph_objs as go

import plotly.plotly as py
from plotly.graph_objs import *
import plotly.dashboard_objs as dashboard

import numpy as np

# local repo
import plotly_toolbox as pltly

plotly.tools.set_credentials_file(username='LouisDge', api_key='GhcHOWrYTxpQr8fhFfWj')

# TODO once the dashboard is created: retrieve plots, webpage, texts etc. and only at this moment, generate dashboard
"""
trace0 = Scatter(
    x=[1, 2, 3, 4],
    y=[10, 15, 13, 17]
)
trace1 = Scatter(
    x=[1, 2, 3, 4],
    y=[16, 5, 11, 9]
)
data = Data([trace0, trace1])

# Online plot
url_2 = py.plot(data, filename = 'basic-line')

# Offline plot
plotly.offline.plot({
    "data": [Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],
    "layout": Layout(title="hello world")
})
"""

# Dashboard
my_dboard = dashboard.Dashboard()

# Plot 1
colorscale = [[0, '#FAEE1C'], [0.33, '#F3558E'], [0.66, '#9C1DE7'], [1, '#581B98']]
trace1 = go.Scatter(
    y = np.random.randn(500),
    mode='markers',
    marker=dict(
        size='16',
        color = np.random.randn(500),
        colorscale=colorscale,
        showscale=True
    )
)
data_1 = [trace1]
url_1 = py.plot(data_1, filename='scatter-for-dashboard', auto_open=False)

# Display
# py.iplot(data_1, filename='scatter-for-dashboard')

# Plot 2
trace0 = Scatter(
    x=[1, 2, 3, 4],
    y=[10, 15, 13, 17]
)
trace1 = Scatter(
    x=[1, 2, 3, 4],
    y=[16, 5, 11, 9]
)
data_2 = Data([trace0, trace1])

# Online plot
url_2 = py.plot(data_2, filename='basic-line', auto_open=False)

# Text
text_for_box = """
## Distributions:


#### Scatter Plot
1. Ranging 0 - 500
2. Even distribution

#### Box Plot
1. Similar Range
2. Outliers present in trace 1 and trace 3

You can view more markdown tips [here](https://daringfireball.net/projects/markdown/syntax).
"""

# Insert plot in Dashboard
fileId_1 = pltly.fileId_from_url(url_1)
fileId_2 = pltly.fileId_from_url(url_2)

box_1 = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': fileId_1,
    'title': 'scatter-for-dashboard'
}

box_2 = {
    'type': 'box',
    'boxType': 'plot',
    'fileId': fileId_2,
    'title': 'simple plot'
}

box_3 = {
    'type': 'box',
    'boxType': 'text',
    'text': text_for_box,
    'title': 'Markdown Options for Text Box'
}

# Layout
my_dboard.insert(box_1)
my_dboard.insert(box_2, 'above', 1)
my_dboard.insert(box_3, 'left', 2)


# Name of the Dashboard
# my_dboard['layout']['first']['first']['first']['text'] = "Dashboard Test 1"

# Add the dashboard to my account
py.dashboard_ops.upload(my_dboard, 'My First Dashboarrd with Python')




