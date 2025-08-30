from app import create_app, db
from app.models import Contact
from sqlalchemy import inspect

def init_db():
    app = create_app()
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        print("Banco de dados inicializado com sucesso!")
        
        # Verifica se as tabelas foram criadas
        print("\nTabelas criadas:")
        inspector = inspect(db.engine)
        print(inspector.get_table_names())
        
        # Conta os contatos
        try:
            count = Contact.query.count()
            print(f"\nTotal de contatos: {count}")
        except Exception as e:
            print(f"\nErro ao contar contatos: {e}")

if __name__ == '__main__':
    init_db()