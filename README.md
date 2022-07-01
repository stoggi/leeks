


cat data.cypherl | docker compose exec neo4j cypher-shell



mutation {
  person: createPerson(params: {name:"Jeremy", email:"jeremy@email.com"}) { person { id } }
  asset: createAsset(params: {name:"Database"}) { asset { id } }
  endpoint: createEndpoint(params: {name:"Jeremy's Macbook Pro"}) { endpoint { id } }
  browser: createBrowser(params: {name:"Chrome", major:99, minor: 1}) { browser { id } }
  operatingSystem: createOperatingSystem(params: {name:"MacOS", major:14, minor:1}) { operatingSystem {id}}
  service: createService(params: {name:"Dropbox"}) { service {id}}
  impact: createImpact(params:{name:"Loss of company" value: 999}) {impact { id }}
}

MATCH (n)
WHERE (n:Team) or (n:Person) or (n:Service)
with collect(n) as nodes, collect(ID(n)) as listNodes
CALL{
  with nodes,listNodes
  unwind nodes as x
  match(x)-[r]-(c)
  where ID(c) in listNodes
  return x,r,c
  }
return x,r,c



MATCH (p:Person)
MATCH (t:Team)
MATCH (s:Service)
RETURN p,t,s

MATCH (t:Team), (p:Person), (s:Service)
OPTIONAL MATCH members=(p)-[:member_of]->(t), owners=(p)-[:owns]->(s)
RETURN t, p, s, members, owners


MATCH (p:Person) WHERE NOT (p)-[:member_of]->(:Team) RETURN p
MATCH (s:Service) WHERE NOT (:Person)-[:owns]->(s) RETURN s

MATCH (p:Person)-[:owns]->(s:Service) WHERE count(p) > 1 RETURN s, p


MATCH (p:Person)-[:owns]->(s:Service)
WITH s as service, count(p) as num_owners, collect(p) as owners
WHERE num_owners > 1
RETURN service, owners




MATCH p=(:Team)<-[:member_of]-(:Person)-[:owns]-(:Service) RETURN p


MATCH p=(:Service)-[*..10]->(:Impact) RETURN p
MATCH p=(:Service)-[*..10]->(:Impact { name:'LoseCompany' }) RETURN p



MATCH (t:Team {name: "Engineering"})
MATCH (s:Service {name: "AWS"})
CREATE (r:Role { name: "Developer" })
CREATE (t)-[:member_of]->(r)
CREATE (r)-[:can_access]->(s)


MATCH (t:Team {name: "Marketing"})
MATCH (s:Service {name: "AWS"})
CREATE (r:Role { name: "ReadOnly" })
CREATE (t)-[:member_of]->(r)
CREATE (r)-[:can_access]->(s)


MATCH p=(:Person)-[:member_of*1..4]->(:Role)-[:can_access]->(:Service {name:"AWS"}) RETURN p


MATCH (p:Person { name: "Bonnie"})
MATCH (s:Service { name: "AWS" })
MATCH authorized=(p)-[:member_of*1..4]->(:Role)-[:can_access]->(s)
OPTIONAL MATCH impacted=(s)-[]->(:Asset)-[]->(i:Impact { name: "LoseCompany"})
RETURN authorized, impacted


MATCH (p:Person { name: "Bonnie"})
MATCH (s:Service { name: "AWS" })
MATCH authorized=(p)-[:member_of*1..4]->(:Role)-[:can_access]->(s)
OPTIONAL MATCH impacted=(s)-[]->(:Asset)-[]->(i:Impact)
RETURN authorized, collect(distinct i.name)


MATCH (p:Person)
MATCH (s:Service { name: "AWS" })
MATCH authorized=(p)-[:member_of*1..4]->(:Role)-[:can_access]->(s)
OPTIONAL MATCH impacted=(s)-[]->(:Asset)-[]->(i:Impact {name: "LoseCompany"})
RETURN authorized, impacted