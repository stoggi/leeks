from ariadne import graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, render_template, flash, url_for, g
from authlib.integrations.flask_client import OAuth

from leeks import resolvers, type_defs
from neo4j import GraphDatabase

schema = make_executable_schema(type_defs, *resolvers)

app = Flask(__name__, static_folder='public', static_url_path='')
app.config.from_mapping(
    SECRET_KEY="dev",
)
app.config.from_prefixed_env("FLASK")

oauth = OAuth(app)
github = oauth.register(
    name='github',
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
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



@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return github.authorize_redirect("http://localhost:5000/authorize")

@app.route('/authorize')
def authorize():
    token = github.authorize_access_token()
    # you can save the token into database
    resp = github.get('/user/emails', token=token)
    resp.raise_for_status()
    profile = resp.json()
    return jsonify(profile)

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
            from { id label name }
            to { id label name }
            edge { id label }
        }
    }
    """)
    
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    if not success:
        for error in result.get("errors", []):
            flash(error["message"])

    return render_template('graph.html', data=result.get("data",{}))

driver = GraphDatabase.driver("neo4j://neo4j:7687", auth=("neo4j", "password"))

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
