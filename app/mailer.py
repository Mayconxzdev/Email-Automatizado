import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging
from dotenv import load_dotenv

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_user)
        self.rate_limit = 30  # emails por minuto
        self.delay = 60 / self.rate_limit  # delay em segundos
        
        if not all([self.smtp_user, self.smtp_password]):
            raise ValueError("SMTP_USER e SMTP_PASSWORD devem ser configurados no .env")
    
    def _connect_smtp(self):
        """Estabelece conexão com o servidor SMTP"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor SMTP: {e}")
            raise
    
    def send_email(self, to_email, subject, html_content, plain_text=None, max_retries=3):
        """
        Envia um e-mail com até 3 tentativas
        
        Args:
            to_email: Email do destinatário
            subject: Assunto do e-mail
            html_content: Conteúdo HTML do e-mail
            plain_text: Versão em texto puro (opcional)
            max_retries: Número máximo de tentativas
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        if not plain_text:
            # Tenta criar uma versão de texto puro removendo as tags HTML
            import re
            plain_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Cria a mensagem
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Anexa as versões de texto e HTML
        part1 = MIMEText(plain_text, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Tenta enviar o e-mail com retry
        for attempt in range(max_retries):
            try:
                server = self._connect_smtp()
                server.send_message(msg)
                server.quit()
                logger.info(f"E-mail enviado para {to_email}")
                return True, "E-mail enviado com sucesso"
            except Exception as e:
                logger.error(f"Tentativa {attempt + 1}/{max_retries} falhou para {to_email}: {e}")
                if attempt == max_retries - 1:
                    return False, str(e)
                time.sleep(2)  # Espera 2 segundos antes de tentar novamente
    
    def send_bulk_emails(self, contacts, subject_template, html_template, dry_run=False):
        """
        Envia e-mails em massa para uma lista de contatos
        
        Args:
            contacts: Lista de dicionários com 'nome' e 'email'
            subject_template: Template para o assunto (usando .format())
            html_template: Template HTML do e-mail (usando .format())
            dry_run: Se True, apenas simula o envio
            
        Returns:
            List[dict]: Resultados do envio para cada contato
        """
        results = []
        
        for i, contact in enumerate(contacts):
            try:
                # Prepara o conteúdo do e-mail
                subject = subject_template.format(**contact)
                html_content = html_template.format(**contact)
                
                # Se for dry run, apenas registra
                if dry_run:
                    logger.info(f"[DRY RUN] Enviando para {contact['email']} - {subject}")
                    status = "dry_run"
                    error_msg = ""
                else:
                    # Envia o e-mail de verdade
                    success, error_msg = self.send_email(
                        to_email=contact['email'],
                        subject=subject,
                        html_content=html_content
                    )
                    status = "sent" if success else "failed"
                    
                    # Respeita o rate limit
                    if i < len(contacts) - 1:  # Não espera após o último e-mail
                        time.sleep(self.delay)
                
                # Registra o resultado
                result = {
                    'nome': contact.get('nome', ''),
                    'email': contact['email'],
                    'assunto': subject,
                    'status': status,
                    'erro': error_msg,
                    'data': datetime.now().isoformat()
                }
                results.append(result)
                
                # Salva o log no CSV
                self._save_to_log(result)
                
            except Exception as e:
                logger.error(f"Erro ao processar contato {contact.get('email')}: {e}")
                results.append({
                    'nome': contact.get('nome', ''),
                    'email': contact.get('email', ''),
                    'assunto': 'Erro ao processar',
                    'status': 'failed',
                    'erro': str(e),
                    'data': datetime.now().isoformat()
                })
        
        return results
    
    def _save_to_log(self, result):
        """Salva o resultado do envio em um arquivo CSV"""
        import csv
        import os
        
        log_file = 'sent_log.csv'
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=result.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
