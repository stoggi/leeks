from xml.dom import NotFoundErr
from ariadne import QueryType, MutationType, graphql_sync, gql, make_executable_schema
from ariadne import InterfaceType, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash
import json
import age
from age.gen.AgtypeParser import *
import psycopg2.extras

GRAPH_NAME = "test_graph"
DSN = "host=localhost port=5432 dbname=postgres user=postgres password=password"

ag = age.connect(graph=GRAPH_NAME, dsn=DSN, cursor_factory=psycopg2.extras.DictCursor)
ag.setGraph(GRAPH_NAME)

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

    type Query {
        persons: [Person]!
        endpoints: [Endpoint]!
        servers: [Server]!

        operatingSystemsUsedByPersons: [OperatingSystemUsedByPerson]

        relationships: [Relationship]!
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

# ...and assign our resolver function to its "hello" field.
@query.field("persons")
def resolve_persons(_, info, first=10, offset=0):
    cursor = ag.execCypher("MATCH (n:Person) RETURN n")
    return (
        agtype_to_dict(row[0])
        for row in cursor
    )

@query.field("relationships")
def resolve_relationships(_, info):
    cursor = ag.execCypher("MATCH (n)-[r]->(m) RETURN n, r, m", cols=["n", "r", "m"])
    return (
        {
            "from": agtype_to_dict(row["n"]),
            "to": agtype_to_dict(row["m"]),
            "edge": agtype_to_dict(row["r"]),
        }
        for row in cursor
    )

@query.field("operatingSystemsUsedByPersons")
def resolve_operating_systems_used_by_persons(_, info):
    cursor = ag.execCypher(
        "MATCH (n:OperatingSystem)<-[r:HasVersion]-(:Endpoint)<-[:Registered]-(p:Person) RETURN n, collect(p)",
        cols=["n", "p"]
    )
    return (
        { 
            "operatingSystem": agtype_to_dict(row["n"]),
            "persons": ( agtype_to_dict(p) for p in row["p"] ),
        } 
        for row in cursor
    )

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
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()

    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
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

if __name__ == "__main__":
    app.run(debug=True)
