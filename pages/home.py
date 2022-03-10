# -*- coding: utf-8 -*-

"""
FAIRifier's home page
"""

from dash import html


# ------------------------------------------------------------------------------
# Homepage layout
# ------------------------------------------------------------------------------
layout = html.Div([
    html.H1('Home'),
    html.Hr(),
    html.P('Welcome to the FAIRifier portal!')
])