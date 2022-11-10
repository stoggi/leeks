from ariadne import InterfaceType, ObjectType, UnionType, QueryType, MutationType
from flask import g

from .utils import node_to_dict, edge_to_dict

query = QueryType()
mutation = MutationType()


@query.field("relationships")
def resolve_relationships(context, info):
    result = g.session.run("""
        MATCH (n)-[r]->(m) RETURN {
            from: { id: ID(n), label: labels(n)[0], name: n.name },
            edge: { id: ID(r), label: type(r) },
            to: { id: ID(m), label: labels(m)[0], name: m.name }
        }
    """)
    return result.value()

@mutation.field("registerEndpoint")
def resolve_register_endpoint(context, info, params):
    result = g.session.run(
        """
        MERGE (e:Endpoint { name: $params.endpoint.name })
        ON CREATE SET e.id = randomUUID(), e += $params.endpoint
        ON MATCH SET e += $params.endpoint
        MERGE (o:OperatingSystem { name: $params.operatingSystem.name, version: $params.operatingSystem.version } )
        ON CREATE SET o.id = randomUUID(), o += $params.operatingSystem
        MERGE (p:Person { email: $params.person.email })
        ON CREATE SET p.id = randomUUID(), p += $params.person
        ON MATCH SET p += $params.person
        MERGE (p)-[:registered]->(e)
        MERGE (e)-[:has]->(o)
        RETURN
        e as endpoint, o as operatingSystem, p as person
        """,
        params=params,
    ).single()
    return result.data()

resolvers = [
    query,
    mutation,
]
