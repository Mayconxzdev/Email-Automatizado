from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        # Cria todas as tabelas se não existirem
        db.create_all()
        # Aplica as migrações pendentes
        from flask_migrate import upgrade
        upgrade()
    
    app.run(debug=True)
