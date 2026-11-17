from geo_semantic_mapper.graph_builder import Literal,Dataset,ATKIS,MAPPING,OSM,dataset,osm_graph,atkis_graph,mapping_graph
from copy import deepcopy
from rdflib.namespace import RDF,SKOS

def test_unique_iri():
    unique_set = set()
    for graph in dataset.graphs():
        assert graph.identifier not in unique_set, "IRI is not unique" 
        unique_set.add(graph.identifier)        
def test_graph_isolation():
    test_dataset = deepcopy(dataset)
    test_osm = test_dataset.graph(OSM["graph"])
    test_atkis = test_dataset.graph(ATKIS["graph"])
    test_mapping = test_dataset.graph(MAPPING["graph"])

    test_tuple = (OSM.ResidentialRoad,RDF.type,SKOS.Concept)
    test_osm.add(test_tuple)

    assert test_tuple not in test_atkis and test_tuple not in test_mapping,"isolation failed"
    assert test_tuple in test_osm,"insert failed"
def test_osm_tag():
    test_dataset = deepcopy(dataset)
    test_osm = test_dataset.graph(OSM["graph"])
    assert (
        OSM.ResidentialRoad,
        OSM.tagKey,
        Literal("highway")
    ) in test_osm

    assert (
        OSM.ResidentialRoad,
        OSM.tagValue,
        Literal("residential")
    ) in test_osm