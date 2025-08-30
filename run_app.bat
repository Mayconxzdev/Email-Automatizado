@echo off
echo Iniciando o servidor de e-mails...
echo.

:: Verifica se o arquivo .env existe
if not exist .env (
    echo Arquivo .env não encontrado. Copiando de .env.example...
    copy .env.example .env
    echo Por favor, configure as variáveis de ambiente no arquivo .env
    pause
    exit /b 1
)

:: Ativa o ambiente virtual (se existir)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Criando ambiente virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Instalando dependências...
    pip install --upgrade pip
    pip install -r requirements.txt
)

:: Cria a pasta de uploads se não existir
if not exist uploads mkdir uploads

:: Inicia o servidor Flask
set FLASK_APP=app
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

pause
