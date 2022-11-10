from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('service')
def resolve_service(context, info):
    result = g.session.run("MATCH (n:Service) RETURN n")
    return result.value()

@mutation.field('createService')
def resolve_create_service(context, info, params):
    result = g.session.run(
        "CREATE (n:Service { id: randomUUID() }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "service": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateService')
def resolve_update_service(context, info, params):
    result = g.session.run(
        "MATCH (n:Service { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "service": result.value() }
    else:
        return { "error": "not found." }