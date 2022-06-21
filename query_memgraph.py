from mgclient import connect
conn = connect(host='127.0.0.1', port=7687)
cursor = conn.cursor()


cursor.execute("""
        MATCH (n)-[r]->(m)
        RETURN n as from, r as edge, m as to
    """)
for n, r, m in iter(cursor.fetchone, None):
    print(n, r, m)