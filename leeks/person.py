from ariadne import QueryType, MutationType
from flask import g
import secrets

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field('person')
def resolve_person(context, info):
    result = g.session.run("MATCH (n:Person) RETURN n")
    return result.value()

@mutation.field('createPerson')
def resolve_create_person(context, info, params):
    verify_token = secrets.token_hex(16)
    result = g.session.run(
        "CREATE (n:Person { id: randomUUID(), verify_token: $verify_token, email_verified: false }) SET n += $params RETURN n",
        params=params,
        verify_token=verify_token,
    ).single()
    if result:
        return { "person": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updatePerson')
def resolve_update_person(context, info, params):
    result = g.session.run(
        "MATCH (n:Person { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "person": result.value() }
    else:
        return { "error": "not found." }