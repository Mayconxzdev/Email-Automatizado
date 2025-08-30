from app import create_app, db
from app.models import Contact

def test_database():
    app = create_app()
    with app.app_context():
        # Verifica se a tabela existe
        print("Tabelas no banco de dados:", db.engine.table_names())
        
        # Conta quantos contatos existem
        count = Contact.query.count()
        print(f"Total de contatos no banco: {count}")
        
        # Lista os contatos
        if count > 0:
            print("\nLista de contatos:")
            for contato in Contact.query.all():
                print(f"- {contato.name} ({contato.email})")
        else:
            print("Nenhum contato encontrado no banco de dados.")

if __name__ == "__main__":
    test_db()
