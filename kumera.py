import os 
from ariadne import graphql_sync, gql, make_executable_schema, load_schema_from_path
from ariadne import InterfaceType, ObjectType, QueryType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash, g

from kumera import resolvers, type_defs
from kumera.utils import node_to_dict, edge_to_dict

from neo4j import GraphDatabase

# Create type instance for Query type defined in our schema.
query = QueryType()
mutation = MutationType()

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

schema = make_executable_schema(type_defs, query, *resolvers)

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
    data = dict(query="{ person { name } }")

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
        person {
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
