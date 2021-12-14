from flask import Flask, request
from flask_cors import CORS
from rdflib.term import URIRef
from datasources.triples import SPARQLTripleStore

from fairifier.termmapping import TermMapper

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
# cors = CORS(app, resource={
#     r'/*': {
#         'origins': '*'
#     }
# })

triple_addr = 'http://172.18.22.17:3030/ds'
# endpoint = 'http://172.18.22.17:7201/repositories/data'
mapper = TermMapper(SPARQLTripleStore(triple_addr + '/sparql', update_endpoint=triple_addr + '/update'))

@app.route('/classes', methods=['GET'])
def get_classes():
    unmapped_classes = mapper.get_unmapped_types()

    return {
        'classes': unmapped_classes
    }

@app.route("/values", methods=['GET', 'POST'])
def get_mappables():
    uri = URIRef(request.form.get('type'))
    values = mapper.get_values_for_type(uri)
    targets = mapper.get_terms_for_type(uri)
    mappings = mapper.get_mappings_for_type(uri)

    print(values)

    return {
        'localValues': values, 
        'targets': [{'uri': str(target['uri']), 'label': str(target['label'])} for target in targets], 
        'mappings': {mapping['value']: str(mapping['target']) for mapping in mappings}
    }

@app.route("/add-mapping", methods=['POST'])
def add_mapping():
    source_type = URIRef(request.form.get('type'))
    value = request.form.get('value')
    target = URIRef(request.form.get('target'))

    mapper.add_mapping(target, source_type, value)

    mappings = mapper.get_mappings_for_type(URIRef(source_type))

    return {
        'mappings': {mapping['value']: str(mapping['target'])for mapping in mappings}
    }

if __name__ == "__main__":
    app.run(debug=True)