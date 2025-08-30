import os
import sys
import logging
from app import create_app, db
from flask_migrate import Migrate

# Configuração de logging detalhada
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Iniciando a aplicação em modo de depuração...")
        
        # Cria o aplicativo
        app = create_app()
        
        # Configura o Flask-Migrate
        migrate = Migrate(app, db)
        
        # Cria o contexto da aplicação
        with app.app_context():
            logger.info("Criando/Verificando banco de dados...")
            
            # Tenta criar as tabelas
            try:
                db.create_all()
                logger.info("Tabelas criadas/verificadas com sucesso!")
                
                # Lista as tabelas existentes
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                logger.info(f"Tabelas no banco de dados: {tables}")
                
                # Tenta inserir um registro de teste
                try:
                    from app.models import Contact
                    contato = Contact.query.filter_by(email="teste@example.com").first()
                    if not contato:
                        contato = Contact(
                            name="Teste",
                            email="teste@example.com",
                            telefone="123456789"
                        )
                        db.session.add(contato)
                        db.session.commit()
                        logger.info("Registro de teste inserido com sucesso!")
                    
                    # Lista os contatos
                    contatos = Contact.query.all()
                    logger.info(f"Total de contatos: {len(contatos)}")
                    
                except Exception as e:
                    logger.error(f"Erro ao inserir/listar contatos: {e}", exc_info=True)
                    
            except Exception as e:
                logger.error(f"Erro ao criar/verificar tabelas: {e}", exc_info=True)
                
        # Inicia o servidor Flask
        logger.info("Iniciando servidor Flask...")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.critical(f"Erro crítico ao iniciar a aplicação: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
