from ariadne import QueryType, MutationType
from flask import g

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field("grafana")
def resolve_grafana(_, info):
    result = g.session.run("MATCH (n)-[r]->(m) WHERE NOT type(r) = 'Follows' RETURN n, r, m")

    nodes = {}
    edges = []
    for n, r, m in result:
        nodes[n.id] = {"id": n.id, "title": ",".join(n.labels), "subtitle": n.properties["name"]}
        nodes[m.id] = {"id": m.id, "title": ",".join(m.labels), "subtitle": m.properties["name"]}
        edges.append({
            "id": r.id,
            "source": n.id,
            "target": m.id,
            "mainstat": r.type,
        })
    return  {
        "nodes": nodes.values(),
        "edges": edges
    }