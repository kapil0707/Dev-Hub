import psycopg2
conn = psycopg2.connect('postgresql://devhub_user:devhub_password_local@localhost:5433/devhub_db')
cur = conn.cursor()
cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('identity', 'automation', 'blob');")
print('TABLES:', cur.fetchall())
