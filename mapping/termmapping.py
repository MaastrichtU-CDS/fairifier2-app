from datasources.triples import SPARQLTripleStore, AbstractTripleSource

from typing import Union
from rdflib.term import URIRef
from functools import cache


class TermMapper():

    def __init__(self, tripleStore: AbstractTripleSource):
        self.tripleStore = tripleStore

    @cache
    def get_unmapped_types(self) -> list[dict[str, Union[str, URIRef]]]:
        # TODO: allow for other roo:local_value predicates
        query = '''
            PREFIX roo: <http://www.cancerdata.org/roo/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?type ?label
            WHERE {
                ?obj rdf:type ?type.
                ?obj roo:local_value ?value .
                OPTIONAL { ?type rdfs:label ?label . }
                FILTER(?type NOT IN (owl:NamedIndividual, owl:Thing)).
            }
            ORDER BY ?type
        '''

        # Alternative query (including check on whether it's been mapped)
        # '''
        # PREFIX roo: <http://www.cancerdata.org/roo/>
        # PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        # PREFIX owl: <http://www.w3.org/2002/07/owl#>
        # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        # PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        # SELECT DISTINCT ?type ?label ?value
        # FROM <http://www.ontotext.com/explicit>
        # WHERE {
        #     ?obj rdf:type ?type.
        #     ?obj roo:local_value ?value .
        #     OPTIONAL { ?type rdfs:label ?label . }
        #     FILTER(?type NOT IN (owl:NamedIndividual, owl:Thing)) .
        #     FILTER NOT EXISTS {
        #         ?type owl:equivalentClass [
        #             rdf:type owl:Class;
        #             owl:intersectionOf [
        #                 rdf:first ?type2;
        #                 rdf:rest [
        #                     rdf:first [
        #                         rdf:type owl:Class;
        #                         owl:unionOf [
        #                             rdf:first [
        #                                 rdf:type owl:Restriction;
        #                                 owl:hasValue ?value;
        #                                 owl:onProperty roo:local_value;
        #                             ];
        #                             rdf:rest rdf:nil;
        #                         ]
        #                     ];
        #                     rdf:rest rdf:nil;
        #                 ]
        #             ]
        #         ]
        #     } .
        # }
        # ORDER BY ?type
        # '''

        results = self.tripleStore.sparql_get(query)

        unmapped = []

        for res in results:
            new = {
                'uri': URIRef(res['type']['value'])
            }
            
            if 'label' in res:
                new['label'] = res['label']['value']

            unmapped.append(new)

        return unmapped

    # @cache
    def get_values_for_class(self, type: URIRef) -> list[str]:
        query = '''
            PREFIX roo: <http://www.cancerdata.org/roo/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT DISTINCT ?value
            WHERE {
                ?obj rdf:type %s .
                ?obj roo:local_value ?value .
            }
            ORDER BY ?type
        ''' % (type.n3())

        return [res['value']['value'] for res in self.tripleStore.sparql_get(query)]

    # @cache
    def get_targets_for_class(self, type: URIRef) -> dict[str, Union[str, URIRef]]:     
        query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT ?subClass ?label 
            WHERE { 
                ?subClass rdfs:subClassOf+ %s .
                ?subClass rdfs:label ?label .
                FILTER(?subClass NOT IN (%s)) .
            }
            ORDER BY ?label
        ''' % (type.n3())

        results = self.tripleStore.sparql_get(query)

        target = []

        for res in results:
            new = {'uri': URIRef(res['subClass']['value'])}

            if 'label' in res:
                new['label'] = res['label']['value']

            target.append(new)

        return target

    def get_mappings_for_class(self, type: URIRef) -> None:
        """Adds a mapping to the database - essentially an 
        equivalent class in OWL that implies any object that has
        type `type` and value `value` belongs to the target class

        Args:
            target (URIRef): the target class (that has meaning in the project)
            type (URIRef): the type of the resource that needs to be mapped
            value ([type]): the value that should be associated with the target class
        """
        # TODO: add support for other local_value preds
        query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX roo: <http://www.cancerdata.org/roo/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT ?value ?target 
            WHERE {
            GRAPH <http://data.local/mapping> {
                ?target owl:equivalentClass [
                    rdf:type owl:Class;
                    owl:intersectionOf [
                        rdf:first <%s>;
                        rdf:rest [
                            rdf:first [
                                rdf:type owl:Class;
                                owl:unionOf [
                                    rdf:first [
                                        rdf:type owl:Restriction;
                                        owl:hasValue ?value;
                                        owl:onProperty roo:local_value;
                                    ];
                                    rdf:rest rdf:nil;
                                ]
                            ];
                            rdf:rest rdf:nil;
                        ]
                    ]
                ].
            }
            FILTER (datatype(?value) = xsd:string)
            }
        """ % (type)

        results = self.tripleStore.sparql_get(query)

        mapping = []

        for res in results:
            new = {
                'value': res['value']['value'],
                'target': res['target']['value']}

            mapping.append(new)

        return mapping

    def add_mapping(self, target: URIRef, type: URIRef, value: str) -> None:
        """Adds a mapping to the database - essentially an 
        equivalent class in OWL that implies any object that has
        type `type` and value `value` belongs to the target class

        Args:
            target (URIRef): the target class (that has meaning in the project)
            type (URIRef): the type of the resource that needs to be mapped
            value ([type]): the value that should be associated with the target class
        """
        # TODO: add support for other local_value preds
        query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX roo: <http://www.cancerdata.org/roo/>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            INSERT {
            GRAPH <http://data.local/mapping> {
                <%s> owl:equivalentClass [
                    rdf:type owl:Class;
                    owl:intersectionOf [
                        rdf:first <%s>;
                        rdf:rest [
                            rdf:first [
                                rdf:type owl:Class;
                                owl:unionOf [
                                    rdf:first [
                                        rdf:type owl:Restriction;
                                        owl:hasValue "%s"^^xsd:string;
                                        owl:onProperty roo:local_value;
                                    ];
                                    rdf:rest rdf:nil;
                                ]
                            ];
                            rdf:rest rdf:nil;
                        ]
                    ]
                ].
            } } WHERE { }
        """ % (target, type, value)

        self.tripleStore.sparql_update(query)
