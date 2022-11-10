from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('endpoint')
def resolve_endpoint(context, info):
    result = g.session.run("MATCH (n:Endpoint) RETURN n")
    return result.value()

@mutation.field('createEndpoint')
def resolve_create_endpoint(context, info, params):
    result = g.session.run(
        "CREATE (n:Endpoint { id: randomUUID() }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "endpoint": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateEndpoint')
def resolve_update_endpoint(context, info, params):
    result = g.session.run(
        "MATCH (n:Endpoint { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "endpoint": result.value() }
    else:
        return { "error": "not found." }