from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('browser')
def resolve_browser(context, info):
    result = g.session.run("MATCH (n:Browser) RETURN n")
    return result.value()

@mutation.field('createBrowser')
def resolve_create_browser(context, info, params):
    result = g.session.run(
        "CREATE (n:Browser { id: randomUUID()} ) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "browser": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateBrowser')
def resolve_update_browser(context, info, params):
    result = g.session.run(
        "MATCH (n:Browser { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "browser": result.value() }
    else:
        return { "error": "not found." }