import sqlite3

def check_db_structure():
    db_path = 'instance/emails.db'
    print(f"Verificando estrutura do banco de dados em: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("Nenhuma tabela encontrada no banco de dados.")
            return
            
        print("\nTabelas encontradas:")
        for table in tables:
            table_name = table[0]
            print(f"\nTabela: {table_name}")
            
            # Lista as colunas da tabela
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                if not columns:
                    print("  - Sem colunas encontradas")
                else:
                    print("  Colunas:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
            except sqlite3.Error as e:
                print(f"  Erro ao obter colunas: {e}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")

if __name__ == "__main__":
    check_db_structure()
