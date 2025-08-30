import os
import sys
from app import create_app, db
from app.models import Contact, EmailLog

def fix_database():
    app = create_app()
    
    with app.app_context():
        print("Criando todas as tabelas...")
        db.create_all()
        
        # Verifica se as tabelas foram criadas
        print("\nTabelas criadas:")
        for table in db.engine.table_names():
            print(f"- {table}")
        
        # Verifica a estrutura da tabela email_log
        print("\nEstrutura da tabela email_log:")
        try:
            columns = db.engine.execute("PRAGMA table_info(email_log)")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
        except Exception as e:
            print(f"Erro ao verificar a tabela email_log: {e}")
        
        # Verifica se podemos inserir dados
        print("\nTestando inserção de dados...")
        try:
            # Cria um contato de teste
            contato = Contact(
                name="Teste",
                email="teste@example.com",
                telefone="123456789"
            )
            db.session.add(contato)
            db.session.commit()
            print("Contato de teste criado com sucesso!")
            
            # Cria um log de e-mail de teste
            log = EmailLog(
                contact_id=contato.id,
                recipient_email=contato.email,
                subject="Teste",
                status="sent"
            )
            db.session.add(log)
            db.session.commit()
            print("Log de e-mail de teste criado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao inserir dados de teste: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_db()
