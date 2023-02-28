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
from datetime import datetime

from app import app
from datasources.triples import SPARQLTripleStore
from mapping.termmapping import TermMapper


# ------------------------------------------------------------------------------
# Inputs
# ------------------------------------------------------------------------------
store = None
mapper = None
classes = None
previous_click = 0


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
    html.Div(id='output-backup-message'),
    html.Div(id='output-restore-message'),
    html.P(),
    html.Hr(),
    html.P(),
    html.H2('Mapping local values'),
    html.P(),
    html.Div(id='input-classes-list'),
    html.Div(id='input-local-values-list'),
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
    global store
    global mapper
    global classes
    if n_clicks > 0:
        # Initialising TerMapper class
        base_addr = os.getenv('TRIPLE_STORE_ADDR')
        base_addr = 'http://localhost:7200' if not base_addr else base_addr
        triple_addr = os.path.join(base_addr, 'repositories', 'data')
        store = SPARQLTripleStore(
            endpoint=triple_addr,
            update_endpoint=triple_addr + '/statements',
            gsp_endpoint=triple_addr + '/rdf-graphs/service'
        )
        mapper = TermMapper(store)

        # Getting unmapped classes
        data_graph = os.getenv('DATA_GRAPH_ADDR')
        data_graph = 'http://localhost/mapping' if not data_graph else \
            data_graph
        onto_graph = os.getenv('ONTOLOGY_GRAPH_ADDR')
        onto_graph = 'http://localhost/ontology' if not onto_graph else \
            onto_graph
        classes = mapper.get_unmapped_types(data_graph, onto_graph)

        # Output for UI
        return html.Div([
            html.Plaintext('Connection established!'),
            html.P(),
            dbc.Button('Get classes', id='get-classes', n_clicks=0),
            dbc.Button('Get mappings', id='get-mappings', n_clicks=0),
            html.P(),
            dbc.Button('Backup', id='backup', n_clicks=0),
            dbc.Button('Restore', id='restore', n_clicks=0)
        ])
    else:
        return html.Plaintext('')


@app.callback(Output('input-classes-list', 'children'),
              Input('get-classes', 'n_clicks'))
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
def get_mapping_options(chosen_class):
    global previous_click
    if chosen_class:
        previous_click = 0
        uri = URIRef(get_class_uri(chosen_class))
        values = mapper.get_values_for_class(uri)
        targets = mapper.get_targets_for_class(uri)
        return html.Div([
            html.H4('Choose local value:'),
            dcc.Dropdown(values, id='input-local-value', multi=True),
            html.H4('Choose target:'),
            dcc.Dropdown([t['label'] for t in targets], id='input-target'),
            html.P(),
            dbc.Button('Add mapping', id='add-button', n_clicks=0)
        ])


@app.callback(Output('output-message', 'children'),
              [Input('add-button', 'n_clicks'),
               Input('input-target', 'value'),
               Input('input-class', 'value'),
               Input('input-local-value', 'value')])
def submit_mapping(n_clicks, target, chosen_class, local_values):
    global previous_click
    if n_clicks > previous_click and local_values and target:
        source_class = URIRef(get_class_uri(chosen_class))
        targets = mapper.get_targets_for_class(source_class)
        target_uri = URIRef(get_target_uri(target, targets))
        if type(local_values) == str: local_values = [local_values]
        for local_value in local_values:
            mapper.add_mapping(target_uri, source_class, local_value)
        previous_click = n_clicks
        return html.Plaintext('Successfully added!')


@app.callback(Output('output-class-mappings-list', 'children'),
              [Input('get-mappings', 'n_clicks')])
def get_class_mappings(n_clicks):
    if n_clicks > 0:
        return html.Div([
            html.H4('Choose class:'),
            dcc.Dropdown(
                [d['label'] for d in classes if len(d) == 2],
                id='input-class-mappings'
            )
        ])


@app.callback(Output('output-backup-message', 'children'),
              [Input('backup', 'n_clicks')])
def get_backup(n_clicks):
    if n_clicks > 0:
        # File to store backup
        now = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = '%s_backup.ttl' % now
        filepath = os.path.join('backup', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Graph with annotations
        url = os.getenv('ANNOTATIONS_GRAPH_ADDR')
        url = 'http://data.local/mapping' if not url else url

        # Get backup
        store.export_file(filepath, URIRef(url))
        return html.Div([
            html.Plaintext('Backup %s successfully saved!' % filename)
        ])


@app.callback(Output('output-restore-message', 'children'),
              [Input('restore', 'n_clicks')])
def restore_from_backup(n_clicks):
    if n_clicks > 0:
        # Find newest backup
        if os.path.exists('backup') and len(os.listdir('backup')) != 0:
            backups = os.listdir('backup')
            backups.sort(reverse=True)
            filepath = os.path.join('backup', backups[0])
        else:
            return html.Div([
                html.Plaintext('There is no backup available!')
            ])

        # Graph with annotations
        url = os.getenv('ANNOTATIONS_GRAPH_ADDR')
        url = 'http://data.local/mapping' if not url else url

        # Restore from backup
        store.import_file(filepath, URIRef(url))
        return html.Div([
            html.Plaintext(f'Successfully restored from %s!' % backups[0])
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
              Input('fade-button', 'n_clicks'))
def get_unmapped_classes(n_clicks):
    if n_clicks > 0 and classes:
        return html.Div([
            dbc.CardBody(
                html.Plaintext(str(json.dumps(classes, indent=4)))
            )
        ])
    else:
        return html.Plaintext('You need to connect to the Triple Store!')
