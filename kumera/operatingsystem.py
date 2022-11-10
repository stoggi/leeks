from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field("operatingSystemsUsedByPersons")
def resolve_operating_systems_used_by_persons(context, info):
    result = g.session.run(
        "MATCH (n:OperatingSystem)<-[r:HasVersion]-(:Endpoint)<-[:Registered]-(p:Person) RETURN n as operatingSystem, collect(p) as persons"
    )
    return result.data()

@query.field('operatingSystem')
def resolve_operatingsystem(context, info):
    result = g.session.run("MATCH (n:OperatingSystem) RETURN n")
    return result.value()

@mutation.field('createOperatingSystem')
def resolve_create_operating_system(context, info, params):
    result = g.session.run(
        "CREATE (n:OperatingSystem { id: randomUUID() }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "operatingSystem": result.value() }
    else:
        return { "error": "unable to create." }

@mutation.field('updateOperatingSystem')
def resolve_update_operating_system(context, info, params):
    result = g.session.run(
        "MATCH (n:OperatingSystem { id: $params.id }) SET n += $params RETURN n",
        params=params,
    ).single()
    if result:
        return { "operatingSystem": result.value() }
    else:
        return { "error": "not found." }