import sqlite3
import os

def test_sqlite():
    try:
        # Caminho para o banco de dados
        db_path = 'email_app.db'
        
        # Remove o arquivo se já existir
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Arquivo antigo {db_path} removido.")
        
        # Conecta ao banco de dados (será criado se não existir)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria uma tabela de teste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Insere um registro de teste
        cursor.execute("INSERT INTO contatos (name, email) VALUES (?, ?)", 
                      ("Teste SQLite", "teste@sqlite.com"))
        
        # Salva as alterações
        conn.commit()
        
        # Lê os registros
        cursor.execute("SELECT * FROM contatos")
        registros = cursor.fetchall()
        
        print("\nRegistros na tabela:")
        for reg in registros:
            print(f"- ID: {reg[0]}, Nome: {reg[1]}, Email: {reg[2]}")
        
        # Fecha a conexão
        conn.close()
        
        print(f"\n✅ Banco de dados criado com sucesso em: {os.path.abspath(db_path)}")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    test_sqlite()
