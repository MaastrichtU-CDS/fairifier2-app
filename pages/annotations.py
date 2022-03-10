# -*- coding: utf-8 -*-

"""
FAIRifier's annotations page
"""

import os
import json

import dash_bootstrap_components as dbc

from dash import html
from dash import dcc
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from rdflib.term import URIRef

from app import app
from datasources.triples import SPARQLTripleStore
from mapping.termmapping import TermMapper


# ------------------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------------------

mapper = None
classes = None
initial_n_clicks = 0


# ------------------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------------------

def get_class_uri(chosen_class):
    global classes
    for c in classes:
        if len(c) == 2:
            if c['label'] == chosen_class:
                return c['uri']


def get_target_uri(chosen_target, targets):
    for target in targets:
        if target['label'] == chosen_target:
            return target['uri']


# ------------------------------------------------------------------------------
# Annotations page layout
# ------------------------------------------------------------------------------

layout = html.Div([
    html.H1('Terminology mapping'),
    html.P(),
    dbc.Button('Connect Triple Store', id='connect-triple-store', n_clicks=0),
    html.Div(id='output-triple-store'),
    html.P(),
    html.Hr(),
    html.P(),
    html.H2('Mapping local values'),
    html.P(),
    html.Div(id='input-classes-list'),
    html.Div(id='input-local-values-list'),
    html.Div(id='input-target-list'),
    html.Div(id='button-add-mapping'),
    html.Div(id='output-message'),
    html.P(),
    html.Hr(),
    html.P(),
    html.H2('Class mappings'),
    html.P(),
    html.Div(id='output-class-mappings-list'),
    html.P(),
    html.Div(id='output-class-mappings'),
    html.P(),
    html.Hr(),
    html.P(),
    html.H2('Unmapped classes'),
    html.P(),
    dbc.Button('Show/Hide', id='fade-button', n_clicks=0),
    dbc.Fade(
        dbc.Card(
            html.Div(id='output-unmapped-classes')
        ),
        id='fade',
        is_in=False,
        appear=False
    )
])


# ------------------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------------------

@app.callback(Output('output-triple-store', 'children'),
              [Input('connect-triple-store', 'n_clicks')])
def connect_to_triple_store(n_clicks):
    global mapper
    global classes
    if n_clicks > 0:
        base_addr = os.getenv('TRIPLE_STORE_ADDR')
        base_addr = 'http://localhost:7200' if not base_addr else base_addr
        triple_addr = os.path.join(base_addr, 'repositories', 'data')
        mapper = TermMapper(
            SPARQLTripleStore(
                endpoint=triple_addr,
                update_endpoint=triple_addr + '/statements'
            )
        )
        classes = mapper.get_unmapped_types()
        return html.Plaintext('Connection established!')
    else:
        return html.Plaintext('')


@app.callback(Output('input-classes-list', 'children'),
              Input('connect-triple-store', 'n_clicks'))
def get_classes_list(n_clicks):
    if n_clicks > 0 and classes:
        return html.Div([
            html.H4('Choose class:'),
            dcc.Dropdown(
                [c['label'] for c in classes if len(c) == 2], id='input-class'
            ),
        ])


@app.callback(Output('input-local-values-list', 'children'),
               Input('input-class', 'value'))
def get_local_values_list(chosen_class):
    if chosen_class:
        uri = URIRef(get_class_uri(chosen_class))
        values = mapper.get_values_for_class(uri)
        return html.Div([
            html.H4('Choose local value:'),
            dcc.Dropdown(values, id='input-local-value')
        ])


@app.callback(Output('input-target-list', 'children'),
               Input('input-class', 'value'))
def get_target_list(chosen_class):
    if chosen_class:
        uri = URIRef(get_class_uri(chosen_class))
        targets = mapper.get_targets_for_class(uri)
        return html.Div([
            html.H4('Choose target:'),
            dcc.Dropdown([t['label'] for t in targets], id='input-target')
        ])


@app.callback(Output('button-add-mapping', 'children'),
              [Input('input-local-value', 'value'),
               Input('input-target', 'value')])
def button_add_mapping(local_value, target):
    if local_value and target:
        return html.Div([
            html.P(),
            dbc.Button('Add mapping', id='add-button', n_clicks=0)
        ])


@app.callback(Output('output-message', 'children'),
              [Input('add-button', 'n_clicks'),
               Input('input-target', 'value'),
               Input('input-class', 'value'),
               Input('input-local-value', 'value')])
def submit_mapping(n_clicks, target, chosen_class, local_value):
    global initial_n_clicks
    # TODO: clear dropdowns after pressing submit
    if n_clicks > initial_n_clicks and local_value and target:
        source_class = URIRef(get_class_uri(chosen_class))
        targets = mapper.get_targets_for_class(source_class)
        target_uri = URIRef(get_target_uri(target, targets))
        mapper.add_mapping(target_uri, source_class, local_value)
        initial_n_clicks = n_clicks
        return html.Plaintext('Successfully added!')


@app.callback(Output('output-class-mappings-list', 'children'),
              Input('connect-triple-store', 'n_clicks'))
def get_class_mappings(n_clicks):
    if n_clicks > 0 and classes:
        return html.Div([
            html.H4('Choose class:'),
            dcc.Dropdown(
                [c['label'] for c in classes if len(c) == 2],
                id='input-class-mappings'
            )
        ])


@app.callback(Output('fade', 'is_in'),
              [Input('fade-button', 'n_clicks')],
              [State('fade', 'is_in')])
def toggle_fade(n, is_in):
    if not n:
        # Button has never been clicked
        return False
    return not is_in


@app.callback(Output('output-class-mappings', 'children'),
              [Input('input-class-mappings', 'value')])
def get_mappings_for_class(chosen_class):
    if chosen_class:
        uri = URIRef(get_class_uri(chosen_class))
        mappings = mapper.get_mappings_for_class(URIRef(uri))
        return html.Plaintext(str(json.dumps(mappings, indent=4)))


@app.callback(Output('output-unmapped-classes', 'children'),
              Input('connect-triple-store', 'n_clicks'))
def get_unmapped_classes(n_clicks):
    if n_clicks > 0 and classes:
        return html.Div([
            dbc.CardBody(
                html.Plaintext(str(json.dumps(classes, indent=4)))
            )
        ])
    else:
        return html.Plaintext('You need to connect to the Triple Store!')
