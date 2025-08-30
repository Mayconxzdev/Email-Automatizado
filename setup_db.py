from app import create_app, db
from app.models import Contact
import os

def setup_database():
    # Garante que a pasta instance existe
    os.makedirs('instance', exist_ok=True)
    
    app = create_app()
    
    with app.app_context():
        # Remove o banco de dados existente (se houver)
        if os.path.exists('instance/email_app.db'):
            try:
                os.remove('instance/email_app.db')
                print("Banco de dados antigo removido.")
            except Exception as e:
                print(f"Erro ao remover banco de dados antigo: {e}")
        
        # Cria todas as tabelas
        print("Criando banco de dados e tabelas...")
        db.create_all()
        
        # Adiciona um contato de teste
        try:
            contato_teste = Contact(
                name="Usuário Teste",
                email="teste@example.com"
            )
            db.session.add(contato_teste)
            db.session.commit()
            print("Contato de teste adicionado com sucesso!")
        except Exception as e:
            print(f"Erro ao adicionar contato de teste: {e}")
        
        # Conta os contatos
        total = Contact.query.count()
        print(f"\nTotal de contatos no banco: {total}")
        
        if total > 0:
            print("\nLista de contatos:")
            for contato in Contact.query.all():
                print(f"- {contato.name} ({contato.email})")

if __name__ == "__main__":
    setup_database()
