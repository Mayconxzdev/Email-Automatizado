import os
import sys
from app import create_app, db
from app.models import Contact, EmailLog

def create_tables():
    app = create_app()
    with app.app_context():
        # Remove o banco de dados existente
        db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
        db_path = os.path.join(db_dir, 'emails.db')
        
        # Garante que o diretório existe
        os.makedirs(db_dir, exist_ok=True)
        
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Banco de dados antigo removido com sucesso!")
            except Exception as e:
                print(f"Erro ao remover o banco de dados antigo: {e}")
                return

        # Cria as tabelas
        try:
            print("\nCriando tabelas...")
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Verifica se as tabelas foram criadas
            from sqlalchemy import inspect
            from sqlalchemy.engine import reflection
            
            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()
            
            if not table_names:
                print("\nAVISO: Nenhuma tabela foi criada!")
                return
                
            print("\nTabelas criadas:")
            for table_name in table_names:
                print(f"\n- {table_name}")
                
                # Obtém as colunas da tabela
                try:
                    columns = inspector.get_columns(table_name)
                    if columns:
                        print("  Colunas:")
                        for col in columns:
                            print(f"    - {col['name']} ({col['type']})")
                    else:
                        print("  Nenhuma coluna encontrada!")
                except Exception as e:
                    print(f"  Erro ao obter colunas: {e}")
            
            # Tenta inserir um registro de teste
            try:
                print("\nInserindo registro de teste...")
                contato = Contact(
                    name="Teste",
                    email="teste@example.com",
                    telefone="123456789"
                )
                db.session.add(contato)
                db.session.commit()
                print("Registro de teste inserido com sucesso!")
                
                # Verifica se o registro foi inserido
                contatos = Contact.query.all()
                print(f"\nTotal de contatos: {len(contatos)}")
                for c in contatos:
                    print(f"- {c.name} ({c.email}) - Tel: {c.telefone}")
                    
            except Exception as e:
                print(f"\nERRO ao inserir registro de teste: {e}")
                db.session.rollback()
                
        except Exception as e:
            print(f"\nERRO ao criar as tabelas: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=== Iniciando criação do banco de dados ===")
    create_tables()
    print("\n=== Processo concluído ===")