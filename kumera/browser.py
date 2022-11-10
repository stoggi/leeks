from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('browser')
def resolve_browser(context, info):
    result = g.session.run("MATCH (n:Browser) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createBrowser')
def resolve_create_browser(context, info, browser):
    result = g.session.run(
        "CREATE (n:Browser { name: $name, major: $major, minor: $minor, patch: $patch }) RETURN n",
        name=browser.get("name", None),
        major=browser.get("major", None),
        minor=browser.get("minor", None),
        patch=browser.get("patch", None),
    )
    return node_to_dict(result.single()["n"])
