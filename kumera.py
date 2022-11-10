from re import M
from ariadne import graphql_sync, gql, make_executable_schema
from ariadne import InterfaceType, ObjectType, QueryType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash, g

import mgclient
from neo4j import GraphDatabase

type_defs = gql("""
    type SoftwareVersion {
        vendor: String!
        version: String!
    }

    enum Role {
        ADMINISTRATOR
        DEVELOPER
        USER
    }

    type Endpoint implements Node {
        id: String!
        label: String!
        name: String!
    }

    type OperatingSystem implements Node {
        id: String!
        label: String!
        name: String!
        version: String!
        major: Int!
        minor: Int!
        patch: Int
        build: String
    }

    type Browser implements Node {
        id: String!
        label: String!
        name: String!
        version: String!
        major: Int!
        minor: Int!
        patch: Int
    }

    type Person implements Node {
        id: String!
        label: String!
        name: String!
        roles: [Role]
    }

    type Server implements Node {
        id: String!
        label: String!
        name: String!
        os: SoftwareVersion!
    }

    interface Node {
        id: String!
        label: String!
        name: String!
    }

    type Edge {
        id: String!
        label: String!
    }

    type Relationship {
        from: Node!
        to: Node!
        edge: Edge!
    }

    type OperatingSystemUsedByPerson {
        operatingSystem: OperatingSystem
        persons: [Person]
    }

    type GrafanaNodeView {
        nodes: [GrafanaNode]
        edges: [GrafanaEdge]
    }

    type GrafanaNode {
        id: String!
        title: String
        subtitle: String
    }

    type GrafanaEdge {
        id: String!
        source: String!
        target: String!
        mainstat: String
    }

    type Query {
        persons: [Person]!
        endpoints: [Endpoint]!
        servers: [Server]!

        operatingSystemsUsedByPersons: [OperatingSystemUsedByPerson]

        relationships: [Relationship]!

        grafana: GrafanaNodeView!

    }
""")

# Create type instance for Query type defined in our schema.
query = QueryType()
mutation = MutationType()
interface_node = InterfaceType("Node")

operating_system = ObjectType("OperatingSystem")
browser = ObjectType("Browser")


def agtype_to_dict(obj):
    return {
        "id": obj.id,
        "label": obj.label,
        **obj.properties,
    }

def node_to_dict(obj):
    return {
        "id": obj.id,
        "label": ",".join(obj.labels),
        **obj,
    }

def edge_to_dict(obj):
    return {
        "id": obj.id,
        "label": obj.type,
        **obj,
    }

# ...and assign our resolver function to its "hello" field.
@query.field("persons")
def resolve_persons(context, info, first=10, offset=0):
    result = g.session.run("MATCH (n:Person) RETURN n")
    return (
        node_to_dict(row["n"])
        for row in result
    )

@query.field("relationships")
def resolve_relationships(context, info):
    result = g.session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
    return (
        {
            "from": node_to_dict(n),
            "to": node_to_dict(m),
            "edge": edge_to_dict(r),
        }
        for n, r, m in result
    )

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

@query.field("grafana")
def resolve_grafana(_, info):
    result = g.session.run("MATCH (n)-[r]->(m) WHERE NOT type(r) = 'Follows' RETURN n, r, m")

    nodes = {}
    edges = []
    for n, r, m in result:
        nodes[n.id] = {"id": n.id, "title": ",".join(n.labels), "subtitle": n.properties["name"]}
        nodes[m.id] = {"id": m.id, "title": ",".join(m.labels), "subtitle": m.properties["name"]}
        edges.append({
            "id": r.id,
            "source": n.id,
            "target": m.id,
            "mainstat": r.type,
        })
    return  {
        "nodes": nodes.values(),
        "edges": edges
    }

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
    if obj["label"] in ["OperatingSystem", "Browser", "Person", "Endpoint"]:
        return obj["label"]
    else:
        return None


schema = make_executable_schema(type_defs, query, interface_node, browser, operating_system)

app = Flask(__name__, static_folder='public', static_url_path='')
app.config.from_mapping(
    SECRET_KEY="dev",
)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()

    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


@app.route('/')
def index():
    data = dict(query="{ persons { name } }")

    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    
    if not success:
        for error in result.get("errors", []):
            flash(error["message"])

    return render_template('persons.html', data=result.get("data",{}))

@app.route('/slides')
def slides():
    return render_template('slides.html')

@app.route('/view')
def view():
    data = dict(query="""
    query relationships {
        relationships {
            from {
                ... nodeFields
            } to { 
                ... nodeFields
            } edge { id label }
        }
        persons {
            ... nodeFields
        }
    }

    fragment nodeFields on Node {
        id
        label
        name
    }
    """)
    
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    if not success:
        for error in result.get("errors", []):
            flash(error["message"])

    return render_template('graph.html', data=result.get("data",{}))

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))

@app.before_request
def connect_mgclient():
    if "c" not in g:
        g.session = driver.session()

@app.teardown_appcontext
def disconnect_mgclient(exception):
    if "c" in g:
        g.session.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
