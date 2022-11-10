from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('person')
def resolve_person(context, info):
    result = g.session.run("MATCH (n:Person) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createPerson')
def resolve_create_person(context, info, person):
    result = g.session.run(
        "CREATE (n:Person { name: $name, email: $email, phone: $phone, roles: $roles }) RETURN n",
        name=person.get("name", None),
        email=person.get("email", None),
        phone=person.get("phone", None),
        roles=person.get("roles", None),
    )
    return node_to_dict(result.single()["n"])
