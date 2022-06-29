from ariadne import QueryType, MutationType, UnionType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('asset')
def resolve_asset(context, info, id=None, name=None):
    result = g.session.run(
        "MATCH (n:Asset) WHERE n.id = $id AND n.name = $name RETURN n",
        id=id,
        name=name,
    )
    return ( node_to_dict(n) for n, in result )


# mutation {
#   createAsset(asset: {name: "jeremy"}) {
#     ... on Asset {
#       id name classification
#     }
#     ... on Error {
#       message
#     }
#   }
# }
@mutation.field('createAsset')
def resolve_create_asset(context, info, asset):
    result = g.session.run(
        "CREATE (n:Asset { name: $name, classification: $classification }) RETURN n",
        name=asset.get("name", None),
        classification=asset.get("classification", None),
    )
    return node_to_dict(result.single()["n"])
