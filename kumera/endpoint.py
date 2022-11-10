from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('endpoint')
def resolve_endpoint(context, info):
    result = g.session.run("MATCH (n:Endpoint) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createEndpoint')
def resolve_create_endpoint(context, info, endpoint):
    result = g.session.run(
        "CREATE (n:Endpoint { name: $name }) RETURN n",
        name=endpoint.get("name", None),
    )
    return node_to_dict(result.single()["n"])
