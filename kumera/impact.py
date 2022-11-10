from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('impact')
def resolve_impact(context, info):
    result = g.session.run("MATCH (n:Impact) RETURN n")
    return result.value()

@mutation.field('createImpact')
def resolve_create_impact(context, info, params):
    result = g.session.run(
        "CREATE (n:Impact { id: randomUUID() }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "impact": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateImpact')
def resolve_update_impact(context, info, params):
    result = g.session.run(
        "MATCH (n:Impact { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "impact": result.value() }
    else:
        return { "error": "not found." }