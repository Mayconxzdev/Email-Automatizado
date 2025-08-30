import pytest
import os
import time
from unittest.mock import patch, MagicMock
from app.mailer import EmailSender
from datetime import datetime

def test_send_email_success():
    """Testa o envio de e-mail com sucesso"""
    with patch('smtplib.SMTP') as mock_smtp:
        # Configura o mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Cria uma instância do EmailSender
        mailer = EmailSender()
        mailer.smtp_user = 'test@example.com'
        mailer.smtp_password = 'testpass'
        mailer.sender_email = 'test@example.com'
        
        # Chama o método de envio
        success, message = mailer.send_email(
            to_email='destinatario@exemplo.com',
            subject='Teste',
            html_content='<h1>Teste</h1>',
            plain_text='Teste'
        )
        
        # Verifica se o e-mail foi enviado com sucesso
        assert success is True
        assert 'sucesso' in message.lower()
        
        # Verifica se os métodos do SMTP foram chamados corretamente
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@example.com', 'testpass')
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

def test_send_email_retry():
    """Testa o mecanismo de tentativa e erro no envio de e-mail"""
    with patch('smtplib.SMTP') as mock_smtp:
        # Configura o mock para falhar duas vezes e depois ter sucesso
        mock_server = MagicMock()
        mock_server.send_message.side_effect = [
            Exception('Erro de conexão'),
            Exception('Timeout'),
            None  # Sucesso na terceira tentativa
        ]
        mock_smtp.return_value = mock_server
        
        mailer = EmailSender()
        mailer.smtp_user = 'test@example.com'
        mailer.smtp_password = 'testpass'
        
        # Chama o método de envio
        success, message = mailer.send_email(
            to_email='destinatario@exemplo.com',
            subject='Teste de Tentativas',
            html_content='<p>Teste de tentativas</p>'
        )
        
        # Verifica se o e-mail foi enviado com sucesso após as tentativas
        assert success is True
        assert mock_server.send_message.call_count == 3

def test_send_bulk_emails_dry_run():
    """Testa o envio em lote no modo de simulação (dry run)"""
    mailer = EmailSender()
    
    # Lista de contatos de teste
    contacts = [
        {'nome': 'Teste 1', 'email': 'teste1@exemplo.com'},
        {'nome': 'Teste 2', 'email': 'teste2@exemplo.com'}
    ]
    
    # Chama o método de envio em lote em modo de teste
    results = mailer.send_bulk_emails(
        contacts=contacts,
        subject_template='Olá, {nome}!',
        html_template='<p>Olá, {nome}!</p>',
        dry_run=True
    )
    
    # Verifica se os resultados estão corretos
    assert len(results) == 2
    assert all(r['status'] == 'dry_run' for r in results)
    assert 'Teste 1' in results[0]['nome']
    assert 'teste1@exemplo.com' in results[0]['email']

def test_rate_limiting():
    """Testa se o rate limiting está funcionando corretamente"""
    mailer = EmailSender()
    mailer.rate_limit = 10  # 10 e-mails por minuto para teste
    mailer.delay = 60 / mailer.rate_limit  # 6 segundos entre cada e-mail
    
    contacts = [
        {'nome': f'Teste {i}', 'email': f'teste{i}@exemplo.com'} 
        for i in range(3)
    ]
    
    start_time = time.time()
    
    with patch.object(mailer, 'send_email') as mock_send:
        mock_send.return_value = (True, 'Enviado')
        mailer.send_bulk_emails(
            contacts=contacts,
            subject_template='Teste',
            html_template='<p>Teste</p>',
            dry_run=False
        )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Verifica se o tempo total foi de pelo menos (n-1) * delay
    # (3 e-mails devem ter 2 intervalos entre eles)
    assert elapsed >= (len(contacts) - 1) * mailer.delay

def test_save_to_log(tmp_path):
    """Testa se o log de envio está sendo salvo corretamente"""
    # Cria um diretório temporário para o teste
    log_file = tmp_path / 'test_log.csv'
    
    mailer = EmailSender()
    mailer.log_file = str(log_file)
    
    # Dados de teste
    result = {
        'nome': 'Teste',
        'email': 'teste@exemplo.com',
        'assunto': 'Assunto de Teste',
        'status': 'sent',
        'erro': '',
        'data': datetime.now().isoformat()
    }
    
    # Chama o método de salvamento de log
    mailer._save_to_log(result)
    
    # Verifica se o arquivo de log foi criado
    assert log_file.exists()
    
    # Verifica o conteúdo do arquivo
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 2  # Cabeçalho + 1 linha de dados
        assert 'Teste' in lines[1]
        assert 'teste@exemplo.com' in lines[1]

# Testes de validação de e-mail
def test_invalid_email():
    """Testa o tratamento de e-mails inválidos"""
    mailer = EmailSender()
    
    with patch('smtplib.SMTP') as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # E-mail inválido
        success, message = mailer.send_email(
            to_email='email-invalido',
            subject='Teste',
            html_content='<p>Teste</p>'
        )
        
        assert success is False
        assert 'inválido' in message.lower()

# Teste de template
def test_template_rendering():
    """Testa a renderização de templates com variáveis"""
    mailer = EmailSender()
    
    contacts = [{
        'nome': 'Fulano',
        'email': 'fulano@exemplo.com',
        'proximo_passos': 'Entre em contato conosco.'
    }]
    
    results = mailer.send_bulk_emails(
        contacts=contacts,
        subject_template='Olá, {nome}!',
        html_template='<p>Seu e-mail é {email}. {proximo_passos}</p>',
        dry_run=True
    )
    
    assert len(results) == 1
    assert 'Olá, Fulano!' in results[0]['assunto']
    assert 'fulano@exemplo.com' in results[0]['conteudo']
    assert 'Entre em contato conosco' in results[0]['conteudo']

# Teste de tratamento de erros
def test_smtp_error_handling():
    """Testa o tratamento de erros do SMTP"""
    with patch('smtplib.SMTP') as mock_smtp:
        # Configura o mock para lançar uma exceção
        mock_smtp.side_effect = Exception('Erro de conexão SMTP')
        
        mailer = EmailSender()
        mailer.smtp_user = 'test@example.com'
        mailer.smtp_password = 'testpass'
        
        success, message = mailer.send_email(
            to_email='destinatario@exemplo.com',
            subject='Teste de Erro',
            html_content='<p>Teste</p>'
        )
        
        assert success is False
        assert 'erro' in message.lower()

# Teste de envio em lote com falhas
def test_bulk_send_with_failures():
    """Testa o envio em lote com alguns e-mails falhando"""
    mailer = EmailSender()
    
    # Configura o mock para falhar em e-mails específicos
    def mock_send_email(to_email, subject, html_content, **kwargs):
        if 'falha' in to_email:
            return False, 'Falha simulada'
        return True, 'Enviado com sucesso'
    
    contacts = [
        {'nome': 'Sucesso 1', 'email': 'sucesso1@exemplo.com'},
        {'nome': 'Falha 1', 'email': 'falha1@exemplo.com'},
        {'nome': 'Sucesso 2', 'email': 'sucesso2@exemplo.com'},
        {'nome': 'Falha 2', 'email': 'falha2@exemplo.com'}
    ]
    
    with patch.object(mailer, 'send_email', side_effect=mock_send_email):
        results = mailer.send_bulk_emails(
            contacts=contacts,
            subject_template='Teste',
            html_template='<p>Teste</p>',
            dry_run=False
        )
    
    # Verifica os resultados
    assert len(results) == 4
    assert sum(1 for r in results if r['status'] == 'sent') == 2
    assert sum(1 for r in results if r['status'] == 'failed') == 2
