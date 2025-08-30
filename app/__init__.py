from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
import sys

# Configuração de logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    try:
        # Configurações
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
        
        # Configura o caminho absoluto para o banco de dados
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'emails.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ECHO'] = True
        
        logger.info(f"Conectando ao banco de dados: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
                # Inicializa extensões
        db.init_app(app)
        migrate = Migrate(app, db)
        
        # Registra blueprints
        from . import routes
        app.register_blueprint(routes.bp)
        
        # Cria tabelas do banco de dados
        with app.app_context():
            logger.info("Criando tabelas do banco de dados...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")
        
        return app
        
    except Exception as e:
        logger.error(f"Erro ao inicializar o aplicativo: {str(e)}", exc_info=True)
        raise
