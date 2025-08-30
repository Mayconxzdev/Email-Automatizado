from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from .models import db, Contact, EmailLog
from .mailer import EmailSender
import pandas as pd
import os
import traceback
from werkzeug.utils import secure_filename
from datetime import datetime

# Configurações
bp = Blueprint('main', __name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

# Garante que a pasta de uploads existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/contatos')
def contatos():
    contatos = Contact.query.order_by(Contact.name).all()
    return render_template('contatos.html', contatos=contatos)

@bp.route('/obter_contato/<int:contato_id>')
def obter_contato(contato_id):
    contato = Contact.query.get_or_404(contato_id)
    return jsonify({
        'id': contato.id,
        'name': contato.name,
        'email': contato.email,
        'telefone': contato.telefone or '',
        'observacoes': contato.observacoes or ''
    })

@bp.route('/adicionar_contato', methods=['POST'])
def adicionar_contato():
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone', '')
    observacoes = request.form.get('observacoes', '')
    
    if not nome or not email:
        return jsonify({'status': 'error', 'message': 'Nome e e-mail são obrigatórios'}), 400
    
    # Verifica se o e-mail já existe
    if Contact.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Este e-mail já está cadastrado'}), 400
    
    # Adiciona o novo contato
    novo_contato = Contact(
        name=nome, 
        email=email,
        telefone=telefone,
        observacoes=observacoes
    )
    db.session.add(novo_contato)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Contato adicionado com sucesso',
        'contato': {
            'id': novo_contato.id, 
            'nome': novo_contato.name, 
            'email': novo_contato.email,
            'telefone': novo_contato.telefone,
            'observacoes': novo_contato.observacoes
        }
    })

@bp.route('/editar_contato/<int:contato_id>', methods=['PUT'])
def editar_contato(contato_id):
    contato = Contact.query.get_or_404(contato_id)
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    telefone = request.form.get('telefone', '')
    observacoes = request.form.get('observacoes', '')
    
    if not nome or not email:
        return jsonify({'status': 'error', 'message': 'Nome e e-mail são obrigatórios'}), 400
    
    # Verifica se o e-mail já existe para outro contato
    outro_contato = Contact.query.filter(Contact.email == email, Contact.id != contato_id).first()
    if outro_contato:
        return jsonify({'status': 'error', 'message': 'Este e-mail já está em uso por outro contato'}), 400
    
    # Atualiza os dados do contato
    contato.name = nome
    contato.email = email
    contato.telefone = telefone
    contato.observacoes = observacoes
    
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Contato atualizado com sucesso',
        'contato': {
            'id': contato.id,
            'nome': contato.name,
            'email': contato.email,
            'telefone': contato.telefone,
            'observacoes': contato.observacoes
        }
    })

@bp.route('/importar_contatos', methods=['POST'])
def importar_contatos():
    if 'arquivo' not in request.files:
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo enviado'}), 400
    
    arquivo = request.files['arquivo']
    sobrescrever = request.form.get('sobrescrever') == 'true'
    
    # Verifica se um arquivo foi selecionado
    if arquivo.filename == '':
        return jsonify({'status': 'error', 'message': 'Nenhum arquivo selecionado'}), 400
    
    # Verifica a extensão do arquivo
    if not allowed_file(arquivo.filename):
        return jsonify({
            'status': 'error',
            'message': 'Formato de arquivo não suportado. Use arquivos .xlsx ou .csv'
        }), 400
    
    # Verifica se o arquivo não está vazio
    arquivo.seek(0, os.SEEK_END)
    tamanho_arquivo = arquivo.tell()
    arquivo.seek(0)  # Volta para o início do arquivo
    
    if tamanho_arquivo == 0:
        return jsonify({'status': 'error', 'message': 'O arquivo está vazio'}), 400
        
    # Limita o tamanho do arquivo para 10MB
    if tamanho_arquivo > 10 * 1024 * 1024:  # 10MB em bytes
        return jsonify({
            'status': 'error',
            'message': 'O arquivo é muito grande. Tamanho máximo permitido: 10MB'
        }), 400
    
    try:
        # Salva o arquivo temporariamente
        filename = secure_filename(arquivo.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"{int(datetime.now().timestamp())}_{filename}")
        arquivo.save(filepath)
        
        # Lê o arquivo
        try:
            if filename.endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:  # CSV
                # Tenta detectar automaticamente o encoding
                try:
                    df = pd.read_csv(filepath, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(filepath, encoding='latin-1')
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Erro ao ler o arquivo: {str(e)}. Verifique se o formato está correto.'
            }), 400
        
        # Converte todos os nomes de colunas para minúsculas
        df.columns = df.columns.str.lower()
        
        # Verifica as colunas necessárias
        required_columns = ['nome', 'email']
        if not all(col in df.columns for col in required_columns):
            return jsonify({
                'status': 'error',
                'message': f'O arquivo deve conter as colunas: {required_columns}. Colunas encontradas: {list(df.columns)}'
            }), 400
        
        # Processa os contatos
        contatos_adicionados = 0
        contatos_atualizados = 0
        contatos_duplicados = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                email = str(row['email']).strip()
                nome = str(row['nome']).strip()
                telefone = str(row['telefone']).strip() if 'telefone' in row and pd.notna(row['telefone']) else ''
                observacoes = str(row['observacoes']).strip() if 'observacoes' in row and pd.notna(row['observacoes']) else ''
                
                # Validação básica
                if not email or not nome:
                    erros.append(f'Linha {index+2}: Nome e e-mail são obrigatórios')
                    continue
                    
                # Verifica se o e-mail já existe
                contato_existente = Contact.query.filter_by(email=email).first()
                
                if contato_existente:
                    if sobrescrever:
                        # Atualiza o contato existente
                        contato_existente.name = nome
                        contato_existente.telefone = telefone
                        contato_existente.observacoes = observacoes
                        contatos_atualizados += 1
                    else:
                        contatos_duplicados += 1
                else:
                    # Cria um novo contato
                    novo_contato = Contact(
                        name=nome,
                        email=email,
                        telefone=telefone,
                        observacoes=observacoes
                    )
                    db.session.add(novo_contato)
                    contatos_adicionados += 1
                    
            except Exception as e:
                erros.append(f'Linha {index+2}: Erro ao processar - {str(e)}')
        
        # Tenta fazer o commit
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Erro ao salvar no banco de dados: {str(e)}'
            }), 500
        
        # Remove o arquivo temporário
        try:
            os.remove(filepath)
        except:
            pass
        
        # Prepara mensagem de sucesso
        mensagem = f'Importação concluída: {contatos_adicionados} adicionados, {contatos_atualizados} atualizados, {contatos_duplicados} duplicados ignorados'
        
        if erros:
            mensagem += f' e {len(erros)} erros encontrados.'
        
        return jsonify({
            'status': 'success',
            'message': mensagem,
            'detalhes': {
                'adicionados': contatos_adicionados,
                'atualizados': contatos_atualizados,
                'duplicados': contatos_duplicados,
                'erros': erros
            }
        })
        
    except Exception as e:
        # Remove o arquivo temporário em caso de erro
        if 'filepath' in locals() and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass
                
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar o arquivo: {str(e)}',
            'traceback': str(traceback.format_exc()) if 'traceback' in locals() else None
        }), 500

@bp.route('/enviar_emails', methods=['POST'])
def enviar_emails():
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data or 'contatos_ids' not in data or 'assunto' not in data or 'conteudo' not in data:
            return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400
        
        contatos_ids = data['contatos_ids']
        assunto = data['assunto']
        conteudo = data['conteudo']
        dry_run = data.get('dry_run', False)
        
        # Obtém os contatos do banco de dados
        contatos = Contact.query.filter(Contact.id.in_(contatos_ids)).all()
        
        if not contatos:
            return jsonify({'status': 'error', 'message': 'Nenhum contato válido selecionado'}), 400
        
        # Prepara os dados para envio
        contatos_para_enviar = []
        for contato in contatos:
            # Verifica se o contato tem e-mail
            if not contato.email:
                continue
                
            # Prepara o conteúdo personalizado para cada contato
            conteudo_personalizado = conteudo
            conteudo_personalizado = conteudo_personalizado.replace('{{nome}}', contato.name or '')
            conteudo_personalizado = conteudo_personalizado.replace('{{email}}', contato.email or '')
            conteudo_personalizado = conteudo_personalizado.replace('{{telefone}}', contato.telefone or '')
            
            contatos_para_enviar.append({
                'nome': contato.name,
                'email': contato.email,
                'conteudo': conteudo_personalizado
            })
        
        if not contatos_para_enviar:
            return jsonify({'status': 'error', 'message': 'Nenhum contato com e-mail válido selecionado'}), 400
        
        # Envia os e-mails
        mailer = EmailSender()
        
        try:
            resultados = []
            
            for contato in contatos_para_enviar:
                try:
                    if dry_run:
                        # Modo de teste - não envia realmente
                        resultados.append({
                            'status': 'dry_run',
                            'email': contato['email'],
                            'message': 'E-mail não enviado (modo de teste)'
                        })
                    else:
                        # Envia o e-mail de verdade
                        mailer.send_email(
                            to_email=contato['email'],
                            subject=assunto,
                            html_content=contato['conteudo']
                        )
                        
                        # Registra o envio no banco de dados
                        novo_log = EmailLog(
                            contact_id=next((c.id for c in contatos if c.email == contato['email']), None),
                            recipient_email=contato['email'],
                            subject=assunto,
                            status='sent',
                            sent_at=datetime.utcnow()
                        )
                        db.session.add(novo_log)
                        
                        resultados.append({
                            'status': 'sent',
                            'email': contato['email'],
                            'message': 'E-mail enviado com sucesso'
                        })
                        
                except Exception as e:
                    # Registra a falha no banco de dados
                    novo_log = EmailLog(
                        contact_id=next((c.id for c in contatos if c.email == contato['email']), None),
                        recipient_email=contato['email'],
                        subject=assunto,
                        status='failed',
                        error_message=str(e),
                        sent_at=datetime.utcnow()
                    )
                    db.session.add(novo_log)
                    
                    resultados.append({
                        'status': 'failed',
                        'email': contato['email'],
                        'message': f'Falha ao enviar e-mail: {str(e)}'
                    })
            
            # Salva todos os logs no banco de dados
            db.session.commit()
            
            # Conta os resultados
            sucessos = sum(1 for r in resultados if r['status'] in ['sent', 'dry_run'])
            falhas = sum(1 for r in resultados if r['status'] == 'failed')
            
            return jsonify({
                'status': 'success',
                'message': f'Envio concluído: {sucessos} enviados, {falhas} falhas',
                'results': resultados
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'status': 'error',
                'message': f'Erro ao enviar e-mails: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar a requisição: {str(e)}'
        }), 500

@bp.route('/excluir_contato/<int:contato_id>', methods=['DELETE'])
def excluir_contato(contato_id):
    try:
        # Busca o contato no banco de dados
        contato = Contact.query.get(contato_id)
        
        if not contato:
            return jsonify({'status': 'error', 'message': 'Contato não encontrado'}), 404
        
        # Remove o contato
        db.session.delete(contato)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Contato excluído com sucesso',
            'contato_id': contato_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Erro ao excluir contato: {str(e)}'
        }), 500

@bp.route('/preview_email', methods=['POST'])
def preview_email():
    data = request.get_json()
    
    if not data or 'assunto' not in data or 'conteudo' not in data or 'contato_id' not in data:
        return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400
    
    # Obtém o contato
    contato = Contact.query.get(data['contato_id'])
    if not contato:
        return jsonify({'status': 'error', 'message': 'Contato não encontrado'}), 404
    
    # Prepara os dados para o template
    dados_contato = {
        'nome': contato.name,
        'email': contato.email,
        'proximo_passos': 'Entre em contato conosco para mais informações.'
    }
    
    # Renderiza o conteúdo
    try:
        conteudo = data['conteudo'].format(**dados_contato)
        assunto = data['assunto'].format(**dados_contato)
        
        return jsonify({
            'status': 'success',
            'assunto': assunto,
            'conteudo': conteudo
        })
    except KeyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar o template: variável {str(e)} não encontrada'
        }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erro ao processar o template: {str(e)}'
        }), 400
