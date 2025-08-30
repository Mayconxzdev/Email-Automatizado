from app import create_app, db
from app.models import Contact
import os
import pandas as pd

# Configura o aplicativo
app = create_app()

def importar_contatos_do_csv(caminho_arquivo):
    """Função para importar contatos de um arquivo CSV"""
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(caminho_arquivo)
        
        # Verifica se as colunas necessárias existem
        if 'nome' not in df.columns or 'email' not in df.columns:
            print("Erro: O arquivo CSV deve conter as colunas 'nome' e 'email'")
            return
        
        # Contadores
        contatos_adicionados = 0
        contatos_duplicados = 0
        
        # Itera sobre as linhas do DataFrame
        for _, row in df.iterrows():
            nome = str(row['nome']).strip()
            email = str(row['email']).strip()
            
            # Verifica se o e-mail já existe
            if not Contact.query.filter_by(email=email).first():
                novo_contato = Contact(name=nome, email=email)
                db.session.add(novo_contato)
                contatos_adicionados += 1
                print(f"Adicionado: {nome} ({email})")
            else:
                contatos_duplicados += 1
                print(f"Duplicado (ignorado): {nome} ({email})")
        
        # Salva as alterações no banco de dados
        db.session.commit()
        
        print(f"\nImportação concluída!")
        print(f"- Contatos adicionados: {contatos_adicionados}")
        print(f"- Contatos duplicados (ignorados): {contatos_duplicados}")
        
    except Exception as e:
        print(f"Erro durante a importação: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        # Cria o banco de dados e as tabelas
        db.create_all()
        print("Banco de dados inicializado com sucesso!")
        
        # Caminho para o arquivo de teste
        caminho_arquivo = 'contatos_teste.csv'
        
        # Verifica se o arquivo existe
        if os.path.exists(caminho_arquivo):
            print(f"\nImportando contatos de: {caminho_arquivo}")
            importar_contatos_do_csv(caminho_arquivo)
        else:
            print(f"\nErro: Arquivo não encontrado: {caminho_arquivo}")
            print("Certifique-se de que o arquivo CSV está no mesmo diretório do script.")
        
        # Mostra todos os contatos no banco de dados
        print("\nContatos no banco de dados:")
        contatos = Contact.query.order_by(Contact.name).all()
        for contato in contatos:
            print(f"- {contato.name} ({contato.email})")
        
        print("\nProcesso concluído.")