# -*- coding: utf-8 -*-

"""
Module with data processing functionalities
"""

import io
import base64

import pandas as pd

from dash import html
from dash import dash_table


def parse_content(content, filename):

    # Decode content
    content_type, content_string = content.split(',')
    decoded = base64.b64decode(content_string)

    # Read input data
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except:
        # TODO: not catching exception properly
        df = None

    return df
