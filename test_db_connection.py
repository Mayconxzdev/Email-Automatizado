from app import create_app, db
from app.models import Contact, EmailLog

def test_connection():
    app = create_app()
    with app.app_context():
        # Verifica se o banco de dados existe
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Conectando ao banco de dados: {db_uri}")
        
        # Tenta criar as tabelas
        try:
            db.create_all()
            print("Tabelas criadas com sucesso!")
            
            # Tenta inserir um registro de teste
            try:
                contato = Contact(
                    name="Teste",
                    email="teste@example.com",
                    telefone="123456789"
                )
                db.session.add(contato)
                db.session.commit()
                print("Contato de teste inserido com sucesso!")
                
                # Verifica se o contato foi inserido
                contatos = Contact.query.all()
                print(f"Total de contatos: {len(contatos)}")
                for c in contatos:
                    print(f"- {c.name} ({c.email})")
                    
            except Exception as e:
                print(f"Erro ao inserir contato de teste: {e}")
                db.session.rollback()
                
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    test_connection()
