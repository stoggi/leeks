from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('impact')
def resolve_impact(context, info):
    result = g.session.run("MATCH (n:Impact) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createImpact')
def resolve_create_impact(context, info, impact):
    result = g.session.run(
        "CREATE (n:Impact { name: $name, value: $value }) RETURN n",
        name=impact.get("name", None),
        value=impact.get("value", None),
    )
    return node_to_dict(result.single()["n"])
