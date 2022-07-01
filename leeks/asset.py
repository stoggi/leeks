from ariadne import QueryType, MutationType, UnionType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('asset')
def resolve_asset(context, info, id=None, name=None):
    result = g.session.run(
        "MATCH (n:Asset) RETURN n",
    )
    return result.value()

@mutation.field('createAsset')
def resolve_create_asset(context, info, params):
    result = g.session.run(
        "CREATE (n:Asset { id: randomUUID()}) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "asset": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateAsset')
def resolve_update_asset(context, info, params):
    result = g.session.run(
        "MATCH (n:Asset { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "asset": result.value() }
    else:
        return { "error": "not found." }