from neo4j import GraphDatabase

driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:

    def test(tx):
        result = tx.run("MATCH (n)-[r]-(m) RETURN n, r, m")
        for r in result:
            print(r['r'].type)
            print({
                "id": r[0]["id"],
                "label": ",".join(r[0].labels),
                **r[0],
            })

    session.read_transaction(test)


with session.begin_transaction() as tx:
    pass

driver.close()