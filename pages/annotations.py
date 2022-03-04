# -*- coding: utf-8 -*-

"""
FAIRifier's annotations page
"""

import json
import pprint

import dash_bootstrap_components as dbc
import pandas as pd

from dash import html
from dash import dcc
from dash import dash_table
from dash.dependencies import Input
from dash.dependencies import Output
from rdflib.term import URIRef

from app import app
from datasources.triples import SPARQLTripleStore
from fairifier.termmapping import TermMapper


inputs = None
triple_addr = 'http://localhost:7200/repositories/data'
mapper = TermMapper(
    SPARQLTripleStore(
        endpoint=triple_addr,
        update_endpoint=triple_addr + '/statements'
    )
)
# ------------------------------------------------------------------------------
# Annotations page layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Terminology mapping'),
    html.Hr(),
    html.P(),
    html.H2('Unmapped classes'),
    html.P(),
    dbc.Button(
        "Get unmapped classes",
        id='unmapped-classes',
        n_clicks=0
    ),
    html.Div(id='output-unmapped-classes'),
])


# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------
@app.callback(Output('output-unmapped-classes', 'children'),
              [Input('unmapped-classes', 'n_clicks')])
def update_unmapped_classes(n_clicks):
    if n_clicks != 0:
        classes = mapper.get_unmapped_types()
        classes = {'Unmapped classes': classes}
        classes = json.dumps(classes, indent=4, sort_keys=True)
    else:
        classes = ''
    return html.Plaintext(str(classes))