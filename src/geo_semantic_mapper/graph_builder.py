from rdflib import Dataset,Namespace,Literal
from rdflib.namespace import RDF, SKOS
from rdflib.namespace import DCTERMS
from rdflib import URIRef

dataset = Dataset()
OSM = Namespace("https://example.org/osm/")
ATKIS = Namespace("https://example.org/atkis/")
MAPPING = Namespace("https://example.org/mapping/")

osm_graph = dataset.graph(identifier=OSM["graph"])
atkis_graph = dataset.graph(identifier=ATKIS["graph"])
mapping_graph = dataset.graph(identifier=MAPPING["graph"])
# concept - skos
osm_graph.add((OSM.ResidentialRoad,RDF.type,SKOS.Concept))
osm_graph.add((OSM.ResidentialRoad,SKOS.prefLabel,Literal("Residential road", lang="en")))
osm_graph.add((OSM.ResidentialRoad,SKOS.definition,Literal("A road primarily serving residential access.", lang="en")))
# tags - value
osm_graph.add((OSM.ResidentialRoad,OSM.tagKey,Literal("highway")))
osm_graph.add((OSM.ResidentialRoad,OSM.tagValue,Literal("residential")))
# provenance
osm_graph.add((
    OSM.ResidentialRoad,
    DCTERMS.source,
    URIRef("https://wiki.openstreetmap.org/wiki/Tag:highway=residential")
))

# model - atkis
atkis_graph.add((ATKIS.AX_Strasse,RDF.type,SKOS.Concept))
atkis_graph.add((ATKIS.AX_Strasse,SKOS.prefLabel,Literal("Straße", lang="de")))
atkis_graph.add((ATKIS.AX_Strasse,ATKIS.objektartkennung,Literal("42002")))
atkis_graph.add((ATKIS.AX_Strasse,DCTERMS.source,URIRef("https://www.adv-online.de/sites/default/files/documents/2026-08/Objektartenkatalog_BasisDLM.html")))
# mapping - candidate
mapping_graph.add((MAPPING.Candidate001,RDF.type,MAPPING.CandidateMapping))
mapping_graph.add((MAPPING.Candidate001,MAPPING.sourceConcept,OSM.ResidentialRoad))
mapping_graph.add((MAPPING.Candidate001,MAPPING.targetConcept,ATKIS.AX_Strasse))
mapping_graph.add((MAPPING.Candidate001,MAPPING.status,MAPPING.pending))         

# add evidence
# mapping_graph.add((MAPPING.Candidate001,MAPPING.hasEvidence,MAPPING.Evidence001))       
# mapping_graph.add((MAPPING.Candidate001,MAPPING.hasEvidence,MAPPING.Evidence002))       
# Evidence001 — Supporting Evidence
mapping_graph.add((MAPPING.Evidence001, RDF.type, MAPPING.EvidenceTemplate))
mapping_graph.add((MAPPING.Evidence001, MAPPING.evidenceType, MAPPING.Supporting))
mapping_graph.add((MAPPING.Evidence001, MAPPING.feature, MAPPING.Surface))
mapping_graph.add((MAPPING.Evidence001, MAPPING.result, MAPPING.Compatible))
mapping_graph.add((MAPPING.Evidence001, MAPPING.generatedBy, MAPPING.R001))

mapping_graph.add((MAPPING.Evidence001, MAPPING.sourceConcept, OSM.ResidentialRoad))
mapping_graph.add((MAPPING.Evidence001, MAPPING.targetConcept, ATKIS.AX_Strasse))

# 比较双方的 Surface，要求任意两个值相等
mapping_graph.add((MAPPING.Evidence001, MAPPING.sourceProperty, OSM.surface))
mapping_graph.add((MAPPING.Evidence001, MAPPING.targetProperty, ATKIS.surface))
mapping_graph.add((MAPPING.Evidence001, MAPPING.operator, MAPPING.Equals))

mapping_graph.add((MAPPING.Evidence002, RDF.type, MAPPING.EvidenceTemplate))
mapping_graph.add((MAPPING.Evidence002, MAPPING.evidenceType, MAPPING.Missing))
mapping_graph.add((MAPPING.Evidence002, MAPPING.feature, MAPPING.Surface))
mapping_graph.add((MAPPING.Evidence002, MAPPING.result, MAPPING.Unknown))
mapping_graph.add((MAPPING.Evidence002, MAPPING.generatedBy, MAPPING.R001))

mapping_graph.add((MAPPING.Evidence002, MAPPING.sourceConcept, OSM.ResidentialRoad))
mapping_graph.add((MAPPING.Evidence002, MAPPING.targetConcept, ATKIS.AX_Strasse))

# 比较双方的 Surface，要求任意两个值相等
mapping_graph.add((MAPPING.Evidence002, MAPPING.sourceProperty, OSM.surface))
mapping_graph.add((MAPPING.Evidence002, MAPPING.targetProperty, ATKIS.surface))
mapping_graph.add((MAPPING.Evidence002, MAPPING.operator, MAPPING.EitherMissing))

# Evidence003 — Conflicting Evidence
mapping_graph.add((MAPPING.Evidence003, RDF.type, MAPPING.EvidenceTemplate))
mapping_graph.add((MAPPING.Evidence003, MAPPING.evidenceType, MAPPING.Conflicting))
mapping_graph.add((MAPPING.Evidence003, MAPPING.feature, MAPPING.Surface))
mapping_graph.add((MAPPING.Evidence003, MAPPING.result, MAPPING.Incompatible))
mapping_graph.add((MAPPING.Evidence003, MAPPING.generatedBy, MAPPING.R001))

mapping_graph.add((MAPPING.Evidence003, MAPPING.sourceConcept, OSM.ResidentialRoad))
mapping_graph.add((MAPPING.Evidence003, MAPPING.targetConcept, ATKIS.AX_Strasse))

mapping_graph.add((MAPPING.Evidence003, MAPPING.sourceProperty, OSM.surface))
mapping_graph.add((MAPPING.Evidence003, MAPPING.targetProperty, ATKIS.surface))
mapping_graph.add((MAPPING.Evidence003, MAPPING.operator, MAPPING.NotEquals))
# rules
# Rule R001 — Surface Comparison
mapping_graph.add((MAPPING.R001, RDF.type, MAPPING.MappingRule))
mapping_graph.add((MAPPING.R001, MAPPING.feature, MAPPING.Surface))
mapping_graph.add((MAPPING.R001, MAPPING.onMatch, MAPPING.Evidence001))
mapping_graph.add((MAPPING.R001, MAPPING.onMissing, MAPPING.Evidence002))
mapping_graph.add((MAPPING.R001, MAPPING.onMismatch, MAPPING.Evidence003))


def evaluate_rule(osm_graph, atkis_graph, mapping_graph, rule_id):
    # 1. 从 Rule 中查找三个分支对应的 Evidence 模板
    branches = [
        MAPPING.onMatch,
        MAPPING.onMismatch,
        MAPPING.onMissing,
    ]
    for branch in branches:
        template = mapping_graph.value(rule_id, branch)
        if template is None:
            continue

        # 2. 从模板读取需要比较的对象、属性和运算符
        source_concept = mapping_graph.value(template, MAPPING.sourceConcept)
        target_concept = mapping_graph.value(template, MAPPING.targetConcept)

        source_property = mapping_graph.value(template, MAPPING.sourceProperty)
        target_property = mapping_graph.value(template, MAPPING.targetProperty)

        operator = mapping_graph.value(template, MAPPING.operator)
        

        # 3. 从 OSM / ATKIS Graph 读取真实值
        source_value = osm_graph.value(source_concept, source_property)
        target_value = atkis_graph.value(target_concept, target_property)
        # print(f"Evaluating {rule_id} with template {template}:")
        # print(f"  Source: {source_concept} - {source_property}")
        # print(f"  Target: {target_concept} - {target_property}")
        # print(f"  Operator: {operator}")
        # print(f"  Source Value: {source_value}")
        # print(f"  Target Value: {target_value}")

        # 4. 执行模板定义的比较条件
        missing = source_value is None or target_value is None

        if operator == MAPPING.EitherMissing:
            matched = missing

        elif missing:
            matched = False

        elif operator == MAPPING.Equals:
            matched = source_value == target_value

        elif operator == MAPPING.NotEquals:
            matched = source_value != target_value

        else:
            raise ValueError(f"Unsupported operator: {operator}")

        # 5. 找到符合条件的 Evidence 模板
        if matched:
            return {
                "rule": rule_id,
                "template": template,
                "source_value": source_value,
                "target_value": target_value,
                "evidence_type": mapping_graph.value(template, MAPPING.evidenceType),
                "result": mapping_graph.value(template, MAPPING.result),
            }

    return None
# res = evaluate_rule(osm_graph, atkis_graph, mapping_graph, MAPPING.R001)
# print(res["result"])  # 输出 Evidence001 的结果

# osm_graph.add((OSM.ResidentialRoad, OSM.surface, Literal("asphalt")))
# atkis_graph.add((ATKIS.AX_Strasse, ATKIS.surface, Literal("asphalt")))
# res = evaluate_rule(osm_graph, atkis_graph, mapping_graph, MAPPING.R001)
# print(res)  # 输出 Evidence001 的结果

def generate_evidence(mapping_graph, candidate, evaluation):
    # 清除这次演示中上一次生成的 Evidence
    old_evidence = mapping_graph.value(candidate, MAPPING.hasEvidence)

    if old_evidence is not None:
        mapping_graph.remove((candidate, MAPPING.hasEvidence, None))
        mapping_graph.remove((old_evidence, None, None))

    evidence = MAPPING.GeneratedEvidence001

    mapping_graph.add((evidence, RDF.type, MAPPING.Evidence))
    mapping_graph.add((evidence, MAPPING.generatedBy, evaluation["rule"]))
    mapping_graph.add((evidence, MAPPING.derivedFromTemplate, evaluation["template"]))
    mapping_graph.add((evidence, MAPPING.evidenceType, evaluation["evidence_type"]))
    mapping_graph.add((evidence, MAPPING.result, evaluation["result"]))

    if evaluation["source_value"] is not None:
        mapping_graph.add((
            evidence, MAPPING.sourceValue, evaluation["source_value"]
        ))

    if evaluation["target_value"] is not None:
        mapping_graph.add((
            evidence, MAPPING.targetValue, evaluation["target_value"]
        ))

    mapping_graph.add((candidate, MAPPING.hasEvidence, evidence))

    return evidence
def make_decision(mapping_graph, candidate, evaluation):
    source = mapping_graph.value(candidate, MAPPING.sourceConcept)
    target = mapping_graph.value(candidate, MAPPING.targetConcept)

    if source is None or target is None:
        raise ValueError("Candidate is missing source or target concept")

    # 清除上一次运行的决策，防止残留
    for relation in (SKOS.exactMatch, SKOS.relatedMatch):
        mapping_graph.remove((source, relation, target))

    result = evaluation["result"]

    if result == MAPPING.Compatible:
        decision = SKOS.exactMatch

    elif result == MAPPING.Unknown:
        decision = SKOS.relatedMatch

    elif result == MAPPING.Incompatible:
        decision = None

    else:
        raise ValueError(f"Unknown evaluation result: {result}")

    if decision is not None:
        mapping_graph.add((source, decision, target))

    # 在 Candidate 上记录决策（NoMapping 是自定义状态）
    mapping_graph.set((
        candidate,
        MAPPING.decision,
        decision if decision is not None else MAPPING.NoMapping
    ))

    return decision
def run_mapping(osm_graph, atkis_graph, mapping_graph):
    candidate = MAPPING.Candidate001

    # Step 1: Rule Evaluation
    evaluation = evaluate_rule(
        osm_graph,
        atkis_graph,
        mapping_graph,
        MAPPING.R001
    )

    if evaluation is None:
        raise ValueError("No matching rule branch")

    # Step 2: Evidence Generation
    evidence = generate_evidence(
        mapping_graph,
        candidate,
        evaluation
    )

    # Step 3: Mapping Decision
    decision = make_decision(
        mapping_graph,
        candidate,
        evaluation
    )

    print("Evidence:", evidence)
    print("Result:", evaluation["result"])
    print("Decision:", decision if decision else "No Mapping")

    return decision

if __name__ == "__main__":

    # Case 1: Equals
    osm_graph.set((OSM.ResidentialRoad, OSM.surface, Literal("asphalt")))
    atkis_graph.set((ATKIS.AX_Strasse, ATKIS.surface, Literal("asphalt")))

    assert run_mapping(osm_graph, atkis_graph, mapping_graph) == SKOS.exactMatch

    # Case 2: Missing
    atkis_graph.remove((ATKIS.AX_Strasse, ATKIS.surface, None))

    assert run_mapping(osm_graph, atkis_graph, mapping_graph) == SKOS.relatedMatch

    # Case 3: NotEquals
    atkis_graph.set((ATKIS.AX_Strasse, ATKIS.surface, Literal("gravel")))

    assert run_mapping(osm_graph, atkis_graph, mapping_graph) is None