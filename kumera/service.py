from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('service')
def resolve_service(context, info):
    result = g.session.run("MATCH (n:Service) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createService')
def resolve_create_service(context, info, service):
    result = g.session.run(
        "CREATE (n:Service { name: $name, website: $website, phone: $phone, email: $email, hours: $hours }) RETURN n",
        name=service.get("name", None),
        website=service.get("website", None),
        phone=service.get("phone", None),
        email=service.get("email", None),
        hours=service.get("hours", None),
    )
    return node_to_dict(result.single()["n"])
