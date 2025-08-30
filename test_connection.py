import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuração de logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        # Usando SQLite em memória para teste
        database_url = "sqlite:///test.db"
        logger.info(f"Tentando conectar ao banco de dados: {database_url}")
        
        engine = create_engine(database_url, echo=True)
        
        # Testa a conexão
        with engine.connect() as conn:
            logger.info("Conexão bem-sucedida!")
            
            # Cria uma tabela de teste
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            """)
            
            # Insere um registro de teste
            conn.execute("INSERT INTO test (name) VALUES ('teste')")
            
            # Lê o registro
            result = conn.execute("SELECT * FROM test").fetchall()
            logger.info(f"Registros na tabela de teste: {result}")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\n✅ Teste de conexão bem-sucedido!")
    else:
        print("\n❌ Falha no teste de conexão.")
