from flask import Flask, request
from rdflib.term import URIRef

from fairifier.termmapping import TermMapper
from fairifier.triplestore import GraphDBTripleStore

app = Flask(__name__)

endpoint = 'http://graphdb:7200/repositories/data'
mapper = TermMapper(GraphDBTripleStore(endpoint))

@app.route('/classes', methods=['GET'])
def get_classes():
    unmapped_classes = mapper.get_unmapped_types()

    return {
        'classes': unmapped_classes
    }

@app.route("/values", methods=['POST'])
def get_mappables():
    data = request.get_json()
    uri = URIRef(data['type'])
    values = mapper.get_values_for_type(uri)
    targets = mapper.get_terms_for_type(uri)
    mappings = mapper.get_mappings_for_type(uri)

    print(mappings)

    return {
        'values': values, 
        'targets': [{'uri': str(target['uri']), 'label': str(target['label'])} for target in targets], 
        'mappings': [{'value': mapping['value'], 'target': str(mapping['target'])} for mapping in mappings]
    }

@app.route("/add-mapping", methods=['POST'])
def add_mapping():
    data = request.get_json()
    source_type = URIRef(data['type'])
    value = data['value']
    target = URIRef(data['target'])

    mapper.add_mapping(target, source_type, value)

    return {'status': 'success'}