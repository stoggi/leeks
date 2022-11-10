from xml.dom import NotFoundErr
from ariadne import QueryType, MutationType, graphql_sync, gql, make_executable_schema
from ariadne import InterfaceType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash
import json
import age
from age.gen.AgtypeParser import *

GRAPH_NAME = "test_graph"
DSN = "host=localhost port=5432 dbname=postgres user=postgres password=password"

ag = age.connect(graph=GRAPH_NAME, dsn=DSN)
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
        major: Int!
        minor: Int!
        patch: Int
        build: String
    }

    type Browser implements Node {
        id: String!
        label: String!
        name: String!
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

    type Query {
        people: [Person]!
        endpoints: [Endpoint]!
        servers: [Server]!

        relationships: [Relationship]!
    }
""")

# Create type instance for Query type defined in our schema.
query = QueryType()
mutation = MutationType()
interface_node = InterfaceType("Node")

# ...and assign our resolver function to its "hello" field.
@query.field("people")
def resolve_people(_, info, first=10, offset=0):
    cursor = ag.execCypher("MATCH (n:Person) RETURN n")
    def result():
        for row in cursor:
            n = row[0]
            yield { "id": n.id, "name": n["name"], "label": n.label, **n.properties }
    return result()

@query.field("relationships")
def resolve_relationships(_, info):
    cursor = ag.execCypher("MATCH p=(n)-[r]->(m) RETURN p")
    def result():
        for row in cursor:
            n, r, m = row[0]
            yield {
                "from": {
                    "id": n.id,
                    "label": n.label,
                    **n.properties,
                },
                "to":{
                    "id": m.id,
                    "label": m.label,
                    **m.properties,
                },
                "edge": {
                    "id": r.id,
                    "label": r.label,
                },
            }
    return result()

@interface_node.type_resolver
def resolve_interface_node(obj, *_):
    if obj["label"] in ["OperatingSystem", "Browser", "Person", "Endpoint"]:
        return obj["label"]
    else:
        return None


schema = make_executable_schema(type_defs, [query, interface_node])

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

    data = dict(query="{ people { name } }")

    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    
    if not success:
        for error in result.get("errors", []):
            flash(error["message"])

    return render_template('people.html', data=result.get("data",{}))

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
        people {
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
