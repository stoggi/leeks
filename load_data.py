import age
from age.gen.AgtypeParser import *

GRAPH_NAME = "test_graph"
DSN = "host=localhost port=5432 dbname=postgres user=postgres password=password"

ag = age.connect(graph=GRAPH_NAME, dsn=DSN)
ag.setGraph(GRAPH_NAME)

ag.execCypher("MATCH (n) DETACH DELETE n")
ag.commit()

ag.execCypher("CREATE (n:Person {name: 'alice', roles: ['DEVELOPER']})")
ag.execCypher("CREATE (n:Person {name: 'bob'})")
ag.execCypher("CREATE (n:Person {name: 'charlie'})")
ag.execCypher("CREATE (n:Person {name: 'dani'})")
ag.execCypher("CREATE (n:Person {name: 'emily'})")
ag.execCypher("CREATE (n:Person {name: 'fred'})")
ag.execCypher("CREATE (n:Person {name: 'greg'})")
ag.execCypher("CREATE (n:Person {name: 'bobby'})")


ag.execCypher("CREATE (n:OperatingSystem {name:'Windows', major:10, minor:2, build:'9943'})")
ag.execCypher("CREATE (n:OperatingSystem {name:'Windows', major:11, minor:1, build:'1234'})")
ag.execCypher("CREATE (n:OperatingSystem {name:'MacOS', major:14, minor:1, build:'21F79', kernel:'21.5.0'})")

ag.execCypher("CREATE (n:Browser {name:'Firefox', major:101, minor: 0, patch: 1})")
ag.execCypher("CREATE (n:Browser {name:'Chrome', major:99, minor: 0, patch: 1})")

ag.commit()

# Create Vertices
ag.execCypher("MATCH (n:Person {name: 'alice'}),(m:Person {name: 'bob'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'bob'}),(m:Person {name: 'fred'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'charlie'}),(m:Person {name: 'bob'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'charlie'}),(m:Person {name: 'dani'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'dani'}),(m:Person {name: 'bob'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'dani'}),(m:Person {name: 'greg'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'emily'}),(m:Person {name: 'fred'}) CREATE (n)-[:Follows]->(m)")
ag.execCypher("MATCH (n:Person {name: 'fred'}),(m:Person {name: 'greg'}) CREATE (n)-[:Follows]->(m)")


ag.execCypher("""
MATCH (n:Person {name: 'alice'})
MERGE (n)-[r:Registered { timestamp: timestamp() }]->(m:Endpoint {name: '1234'})
MERGE (o:OperatingSystem {name:'Windows', major:10, minor:2, build:'9943'})
MERGE (b:Browser {name:'Firefox', major:101, minor: 0, patch: 1})
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(o)
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(b)
""")
ag.execCypher("""
MATCH (n:Person {name: 'bob'})
MERGE (n)-[r:Registered { timestamp: timestamp() }]->(m:Endpoint {name: '2344'})
MERGE (o:OperatingSystem {name:'Windows', major:10, minor:2, build:'9943'})
MERGE (b:Browser {name:'Chrome', major:99, minor: 0, patch: 1})
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(o)
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(b)
""")
ag.execCypher("""
MATCH (n:Person {name: 'charlie'})
MERGE (n)-[r:Registered { timestamp: timestamp() }]->(m:Endpoint {name: '3232'})
MERGE (o:OperatingSystem {name:'Windows', major:11, minor:1, build:'1234'})
MERGE (b:Browser {name:'Chrome', major:99, minor: 0, patch: 1})
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(o)
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(b)
""")
ag.execCypher("""
MATCH (n:Person {name: 'dani'})
MERGE (n)-[r:Registered { timestamp: timestamp() }]->(m:Endpoint {name: '4543'})
MERGE (o:OperatingSystem {name:'MacOS', major:14, minor:1, build:'21F79'})
MERGE (b:Browser {name:'Chrome', major:99, minor: 0, patch: 1})
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(o)
CREATE (m)-[:HasSoftware { timestamp: timestamp() }]->(b)
""")



ag.commit()

cursor = ag.execCypher("MATCH p=(n)-[]->(m)  RETURN p")
for row in cursor:
    print(row[0])
    

