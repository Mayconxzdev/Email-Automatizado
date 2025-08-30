from app import create_app, db
from app.models import Contact

def test_memory_db():
    app = create_app()
    
    with app.app_context():
        # Cria as tabelas
        db.create_all()
        
        # Adiciona um contato de teste
        novo_contato = Contact(name="Teste", email="teste@example.com")
        db.session.add(novo_contato)
        db.session.commit()
        
        # Lista todos os contatos
        contatos = Contact.query.all()
        print("\nContatos no banco de dados:")
        for contato in contatos:
            print(f"- {contato.name} ({contato.email})")
        
        # Conta quantos contatos existem
        total = Contact.query.count()
        print(f"\nTotal de contatos: {total}")

if __name__ == '__main__':
    test_memory_db()
