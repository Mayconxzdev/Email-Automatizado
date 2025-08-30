import sqlite3

# Conecta ao banco de dados
conn = sqlite3.connect('instance/emails.db')
cursor = conn.cursor()

# Lista todas as tabelas
print("Tabelas no banco de dados:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"\nTabela: {table[0]}")
    # Lista as colunas de cada tabela
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print("Colunas:")
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")

conn.close()