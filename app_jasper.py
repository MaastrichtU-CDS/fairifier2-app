import json
from rdflib.term import URIRef
from datasources.triples import SPARQLTripleStore
from fairifier.termmapping import TermMapper


triple_addr = 'http://localhost:7200/repositories/data'
mapper = TermMapper(SPARQLTripleStore(triple_addr,
                                      update_endpoint=triple_addr + '/statements'))

def get_classes():
    unmapped_classes = mapper.get_unmapped_types()

    return {
        'classes': unmapped_classes
    }

def get_local_values(uri):
    uri = URIRef(uri)
    values = mapper.get_values_for_class(uri)
    targets = mapper.get_targets_for_class(uri)
    mappings = mapper.get_mappings_for_class(uri)

    return {
        'localValues': values,
        'targets': [{'uri': str(target['uri']), 'label': str(target['label'])} for target in targets],
        'mappings': {mapping['value']: str(mapping['target']) for mapping in mappings}
    }

def add_mapping(uri, value, target):
    source_class = URIRef(uri)
    target = URIRef(target)

    mapper.add_mapping(target, source_class, value)

    mappings = mapper.get_mappings_for_class(URIRef(source_class))

    return {
        'mappings': {mapping['value']: str(mapping['target'])for mapping in mappings}
    }

if __name__ == "__main__":

    # Get classes
    classes = get_classes()
    print(json.dumps(classes, indent=4))

    # Get local values
    uri = classes['classes'][1]['uri']
    values = get_local_values(uri)
    print(values)

    # Add mapping
    value = values['localValues'][1]
    target = values['targets'][1]['uri']
    mappings = add_mapping(uri, value, target)