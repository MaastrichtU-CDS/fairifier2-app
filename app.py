from flask import Flask, request
from flask_cors import CORS
from rdflib.term import URIRef

from fairifier.termmapping import TermMapper
from fairifier.triplestore import GraphDBTripleStore

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)
# cors = CORS(app, resource={
#     r'/*': {
#         'origins': '*'
#     }
# })

endpoint = 'http://172.18.22.17:3030/ds/sparql'
# endpoint = 'http://172.18.22.17:7201/repositories/data'
mapper = TermMapper(GraphDBTripleStore(endpoint))

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

if __name__ == "__main__":
    app.run(debug=True)