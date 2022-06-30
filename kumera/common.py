from ariadne import InterfaceType, ObjectType, UnionType, QueryType
from flask import g

from .utils import node_to_dict, edge_to_dict

interface_node = InterfaceType("Node")
operating_system = ObjectType("OperatingSystem")
browser = ObjectType("Browser")
query = QueryType()

@browser.field("version")
@operating_system.field("version")
def resolve_version(obj, info):
    major = obj.get("major", 0)
    minor = obj.get("minor", 0)
    patch = obj.get("patch", 0)
    build = obj.get("build", '')
    return "{}.{}.{}.{}".format(major, minor, patch, build)


@interface_node.type_resolver
def resolve_interface_node(obj, *_):
    return obj.get("label", None)


@query.field("relationships")
def resolve_relationships(context, info):
    result = g.session.run("""
        MATCH (n)-[r]->(m) RETURN {
            from: { id: ID(n), label: labels(n)[0], name: n.name },
            edge: { id: ID(r), label: type(r) },
            to: { id: ID(m), label: labels(m)[0], name: m.name }
        }
    """)
    return result.value()


resolvers = [
    query,
    operating_system,
    interface_node,
    browser,
]
