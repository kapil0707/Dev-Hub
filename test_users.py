import psycopg2
conn = psycopg2.connect('postgresql://devhub_user:devhub_password_local@localhost:5433/devhub_db')
cur = conn.cursor()
cur.execute("SELECT id, email, is_active FROM identity.users;")
print('USERS:', cur.fetchall())
