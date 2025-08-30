import os
import sqlite3

def verify_database():
    # Caminho para o banco de dados
    db_path = os.path.join('instance', 'emails.db')
    
    if not os.path.exists(db_path):
        print(f"Erro: O arquivo {db_path} não foi encontrado.")
        return
    
    print(f"Verificando banco de dados em: {os.path.abspath(db_path)}")
    print(f"Tamanho do arquivo: {os.path.getsize(db_path)} bytes")
    
    try:
        # Conecta ao banco de dados
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nTabelas encontradas:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Lista as colunas de cada tabela
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"  Colunas:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar o banco de dados: {e}")

if __name__ == "__main__":
    verify_database()
