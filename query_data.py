import age
import psycopg2.extras
from age.gen.AgtypeParser import *

GRAPH_NAME = "test_graph"
DSN = "host=localhost port=5432 dbname=postgres user=postgres password=password"

ag = age.connect(graph=GRAPH_NAME, dsn=DSN, cursor_factory=psycopg2.extras.DictCursor)
ag.setGraph(GRAPH_NAME)

#cursor = ag.execCypher("MATCH (n)-[:status]->(m:Person {name: 'cool_person'})  RETURN n")
cursor = ag.execCypher("MATCH p=(n)-[r]-(m) RETURN p")
for row in cursor:
    n, r, m = row[0]
    #print(n, r, m)



cursor = ag.execCypher("MATCH (n:OperatingSystem)<-[r:HasVersion]-(:Endpoint)<-[:Registered]-(p:Person) RETURN n, collect(p)", cols=["\"operatingSystem\"", "persons"])
for row in cursor:
    print(dict(row))