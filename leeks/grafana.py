from ariadne import QueryType, MutationType
from flask import g

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field("grafana")
def resolve_grafana(_, info):
    result = g.session.run("MATCH (n)-[r]->(m) WHERE (n:Person) or (n:Team) or (n:Service) RETURN n, r, m LIMIT 20")

    nodes = {}
    edges = []
    for n, r, m in result:
        nodes[n.id] = {"id": n.id, "title": ",".join(n.labels), "subtitle": n["name"]}
        nodes[m.id] = {"id": m.id, "title": ",".join(m.labels), "subtitle": m["name"]}
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