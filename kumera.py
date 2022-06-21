from ariadne import graphql_sync, gql, make_executable_schema
from ariadne import InterfaceType, ObjectType, QueryType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash, g

import mgclient

conn = mgclient.connect(host='127.0.0.1', port=7687)

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

def node_to_dict(obj):
    return {
        "id": obj.id,
        "label": ",".join(obj.labels),
        **obj.properties,
    }

def edge_to_dict(obj):
    return {
        "id": obj.id,
        "label": obj.type,
        **obj.properties,
    }

# ...and assign our resolver function to its "hello" field.
@query.field("persons")
def resolve_persons(context, info, first=10, offset=0):
    c = g.conn.cursor()
    c.execute("MATCH (n:Person) RETURN n")
    return (
        node_to_dict(row[0])
        for row in iter(c.fetchone, None)
    )

@query.field("relationships")
def resolve_relationships(context, info):
    c = g.conn.cursor()
    c.execute("MATCH (n)-[r]->(m) RETURN n, r, m")
    return (
        {
            "from": node_to_dict(n),
            "to": node_to_dict(m),
            "edge": edge_to_dict(r),
        }
        for n, r, m in iter(c.fetchone, None)
    )

@query.field("operatingSystemsUsedByPersons")
def resolve_operating_systems_used_by_persons(context, info):
    c = g.conn.cursor()
    c.execute(
        "MATCH (n:OperatingSystem)<-[r:HasVersion]-(:Endpoint)<-[:Registered]-(p:Person) RETURN n, collect(p)"
    )
    return (
        { 
            "operatingSystem": node_to_dict(n),
            "persons": ( node_to_dict(p) for p in collect_p ),
        } 
        for n, collect_p in iter(c.fetchone, None)
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

@app.before_request
def connect_mgclient():
    if "c" not in g:
        g.conn = mgclient.connect(host='127.0.0.1', port=7687)

@app.teardown_appcontext
def disconnect_mgclient(exception):
    if "c" in g:
        if g.conn.status != mgclient.CONN_STATUS_CLOSED:
            g.conn.close()

if __name__ == "__main__":
    app.run(debug=True)
