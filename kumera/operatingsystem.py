from ariadne import QueryType, MutationType
from flask import g

from .utils import node_to_dict

query = QueryType()
mutation = MutationType()

resolvers = [query, mutation]

@query.field("operatingSystemsUsedByPersons")
def resolve_operating_systems_used_by_persons(context, info):
    result = g.session.run(
        "MATCH (n:OperatingSystem)<-[r:HasVersion]-(:Endpoint)<-[:Registered]-(p:Person) RETURN n, collect(p)"
    )
    return (
        { 
            "operatingSystem": node_to_dict(n),
            "persons": ( node_to_dict(p) for p in collect_p ),
        } 
        for n, collect_p in result
    )

@query.field('operatingSystem')
def resolve_operatingsystem(context, info):
    result = g.session.run("MATCH (n:OperatingSystem) RETURN n")
    return ( node_to_dict(n) for n, in result )

@mutation.field('createOperatingSystem')
def resolve_create_operating_system(context, info, operatingSystem):
    result = g.session.run(
        "CREATE (n:OperatingSystem { name: $name, major: $major, minor: $minor, patch: $patch, build: $build }) RETURN n",
        name=operatingSystem.get("name", None),
        major=operatingSystem.get("major", None),
        minor=operatingSystem.get("minor", None),
        patch=operatingSystem.get("patch", None),
        build=operatingSystem.get("build", None),
    )
    return node_to_dict(result.single()["n"])
