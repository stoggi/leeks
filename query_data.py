import age
from age.gen.AgtypeParser import *

GRAPH_NAME = "test_graph"
DSN = "host=localhost port=5432 dbname=postgres user=postgres password=password"

ag = age.connect(graph=GRAPH_NAME, dsn=DSN)
ag.setGraph(GRAPH_NAME)

#cursor = ag.execCypher("MATCH (n)-[:status]->(m:Person {name: 'cool_person'})  RETURN n")
cursor = ag.execCypher("MATCH p=(n)-[r]-(m) RETURN p")
for row in cursor:
    n, r, m = row[0]
    #print(n, r, m)
