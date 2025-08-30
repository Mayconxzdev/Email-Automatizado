import sqlite3
import os

def test_connection():
    # Caminho para o banco de dados
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    db_path = os.path.join(db_dir, 'test_db.sqlite')
    
    print(f"Tentando criar/abrir o banco de dados em: {db_path}")
    
    # Garante que o diretório existe
    os.makedirs(db_dir, exist_ok=True)
    
    try:
        # Conecta ao banco de dados (será criado se não existir)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria uma tabela de teste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Insere um registro de teste
        cursor.execute("INSERT OR IGNORE INTO test_table (name, email) VALUES (?, ?)", 
                      ("Teste SQLite", "teste@sqlite.com"))
        
        # Salva as alterações
        conn.commit()
        
        # Lê os registros
        cursor.execute("SELECT * FROM test_table")
        registros = cursor.fetchall()
        
        print("\nRegistros na tabela de teste:")
        for reg in registros:
            print(f"- ID: {reg[0]}, Nome: {reg[1]}, Email: {reg[2]}")
        
        # Fecha a conexão
        conn.close()
        
        print(f"\n✅ Banco de dados de teste criado com sucesso em: {db_path}")
        
    except Exception as e:
        print(f"\n❌ Erro ao acessar o banco de dados: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
