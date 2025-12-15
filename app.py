"""
Portal Corporativo Mendonça Galvão Contadores Associados
=========================================================

Aplicação Flask que centraliza o acesso aos sistemas internos da empresa.

Autor: Núcleo Digital MG
Data: 2025-12-09
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from users import User, load_users, save_users, get_user_by_email, update_user_password
from employees import get_employee_info, get_all_employees, is_valid_email_domain, is_employee_registered
from datetime import datetime
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

# Inicializar aplicação Flask
app = Flask(__name__)


# Configuração Segura da Chave Secreta
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuração do Flask-Mail (Console para testes se não houver env vars)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Exemplo padrão
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
# Importante: Se não houver config de email, imprime no console para debug
if not app.config['MAIL_USERNAME']:
    # Modo de Simulação: Não tenta enviar para o servidor SMTP
    app.config['MAIL_SUPPRESS_SEND'] = True
    app.config['MAIL_DEBUG'] = True

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)


# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'


# Caminho para arquivo de usuários removido daqui pois está em users.py

# User class logic moved to users.py
# load_users, save_users, get_user_by_email moved to users.py

@login_manager.user_loader
def load_user(email):
    """Carrega um usuário baseado no email"""
    # Importado de users.py: load_users
    users = load_users()
    user_data = next((u for u in users if u['email'] == email), None)
    
    if user_data:
        return User(user_data['email'], user_data['name'])
    return None

# Funções auxiliares removidas daqui (load_users, save_users, get_user_by_email)

@app.route('/')
@login_required
def index():
    """
    Rota principal que renderiza a landing page.
    
    Esta página centraliza o acesso aos sistemas:
    - Portal do Colaborador
    - Sistema de Cálculo de Comissão
    
    Returns:
        Template HTML renderizado com todos os sistemas disponíveis
    """
    # Dados dos sistemas (podem ser movidos para um arquivo de configuração ou banco de dados)
    sistemas = [
        {
            'id': 'portal-colaborador',
            'titulo': 'Portal do Colaborador',
            'descricao': 'Gerencie suas informações pessoais, contracheques, férias e benefícios de forma rápida e segura.',
            'url': 'https://portalcolabmg.lovable.app/login',
            'icone': 'icon-portal.png',
            'cta': 'Acessar Portal'
        },
        {
            'id': 'sistema-comissao',
            'titulo': 'Sistema de Cálculo de Comissão',
            'descricao': 'Calcule suas comissões de forma automática e transparente, com relatórios detalhados.',
            'url': 'https://calculadp.lovable.app/',
            'icone': 'icon-comissao.png',
            'cta': 'Calcular Comissão'
        },
        {
            'id': 'ponto-eletronico',
            'titulo': 'Processamento Inteligente de Ponto Eletrônico',
            'descricao': 'Faça upload dos espelhos de ponto (PDF ou Imagem). O sistema identifica automaticamente faltas (integrais e parciais), horas extras e adicional noturno.',
            'url': 'https://ai.studio/apps/drive/1-7xvcz9OLnLck0vtStQp4u375oKg4MyV?fullscreenApplet=true',
            'icone': 'icon-ponto.png',
            'cta': 'Processar Ponto'
        },
        {
            'id': 'adiantamento-salarial',
            'titulo': 'Cálculo Automático de Adiantamento',
            'descricao': 'Importe o PDF da folha de pagamento para iniciar o processamento automático de adiantamento salarial mensal.',
            'url': 'https://ai.studio/apps/drive/14NzWtRjoDQhHhwxaDIeZisxTAzIZDkvq?fullscreenApplet=true',
            'icone': 'icon-adiantamento.png',
            'cta': 'Calcular Adiantamento'
        }
    ]
    
    # Membros da Equipe (Núcleo Digital)
    team_members = [
        {
            'nome': 'Tiago Nunes',
            'foto': 'tiago-nunes.jpg'  # Foto real fornecida
        },
        {
            'nome': 'Guilherme Almeida',
            'foto': 'guilherme-almeida.jpg'  # Foto real fornecida
        },
        {
            'nome': 'Eduardo Melo',
            'foto': 'eduardo-melo.jpg'  # Foto real fornecida
        },
        {
            'nome': 'Arthur Monteiro',
            'foto': 'team-member.jpg'  # Foto real fornecida
        }
    ]
    
    return render_template(
        'index.html',
        sistemas=sistemas,
        team_members=team_members,
        current_user=current_user,
        ano_atual=2025  # Pode ser dinâmico: datetime.now().year
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota de login de usuários.
    
    GET: Exibe formulário de login
    POST: Processa autenticação
    """
    # Se já estiver logado, redirecionar para index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        # Validações
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        # Verificar se email tem domínio válido
        if not is_valid_email_domain(email):
            flash('Email deve ser do domínio @mendoncagalvao.com.br', 'error')
            return render_template('login.html')
        
        # Buscar usuário
        user_data = get_user_by_email(email)
        
        if not user_data:
            flash('Email ou senha incorretos.', 'error')
            return render_template('login.html')
        
        # Verificar senha
        if not check_password_hash(user_data['password_hash'], password):
            flash('Email ou senha incorretos.', 'error')
            return render_template('login.html')
        
        # Login bem-sucedido
        user = User(user_data['email'], user_data['name'])
        login_user(user)
        
        # Redirecionar para página solicitada ou index
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Rota de cadastro de novos usuários.
    
    GET: Exibe formulário de cadastro
    POST: Processa cadastro
    """
    # Se já estiver logado, redirecionar para index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validações básicas
        if not all([name, email, password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('register.html')
        
        # Validar domínio do email
        if not is_valid_email_domain(email):
            flash('Email deve ser do domínio @mendoncagalvao.com.br', 'error')
            return render_template('register.html')
        
        # Verificar se email está na base de funcionários
        if not is_employee_registered(email):
            flash('Email não encontrado na base de funcionários. Entre em contato com o RH.', 'error')
            return render_template('register.html')
        
        # Validar senha
        if len(password) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
        
        # Verificar se usuário já está cadastrado
        if get_user_by_email(email):
            flash('Este email já está cadastrado. Faça login.', 'error')
            return redirect(url_for('login'))
        
        # Criar novo usuário
        users = load_users()
        new_user = {
            'email': email,
            'name': name,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        }
        users.append(new_user)
        save_users(users)
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')



# ============================================
# RECUPERAÇÃO DE SENHA
# ============================================

def send_reset_email(user_email, token):
    """Envia e-mail de redefinição de senha com link seguro."""
    msg = Message('Redefinição de Senha - Central de Sistemas',
                  sender='noreply@mgcontadores.com.br',
                  recipients=[user_email])
    
    reset_url = url_for('reset_password', token=token, _external=True)
    
    msg.html = render_template('email/reset_password.html', 
                               reset_url=reset_url,
                               year=datetime.now().year)
    
    # Se estiver em modo de simulação, imprimir o link no console
    if app.config.get('MAIL_SUPPRESS_SEND'):
        print("\n" + "="*50)
        print("SIMULAÇÃO DE EMAIL - LINK DE REDEFINIÇÃO:")
        print(reset_url)
        print("="*50 + "\n")
    
    mail.send(msg)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        
        # Verificar se o e-mail existe na base de usuários
        user = get_user_by_email(email)
        if user:
            # Gerar token seguro com validade de 1 hora (3600 segundos)
            token = serializer.dumps(email, salt='recover-key')
            send_reset_email(email, token)
            flash('Um link de redefinição foi enviado para seu e-mail.', 'info')
        else:
            # Mensagem genérica por segurança
            flash('Se este e-mail estiver cadastrado, você receberá um link.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    try:
        # Validar token (expira em 3600 segundos / 1 hora)
        email = serializer.loads(token, salt='recover-key', max_age=3600)
    except:
        flash('O link de redefinição é inválido ou expirou.', 'error')
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('reset_password', token=token))
            
        if len(password) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'error')
            return redirect(url_for('reset_password', token=token))
            
        # Atualizar senha
        new_hash = generate_password_hash(password)
        if update_user_password(email, new_hash):
            flash('Sua senha foi redefinida com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Erro ao atualizar senha. Usuário não encontrado.', 'error')
            
    return render_template('reset_password.html', token=token)

@app.route('/logout')
@login_required
def logout():
    """
    Rota de logout.
    
    Encerra a sessão do usuário e redireciona para login.
    """
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('login'))


@app.route('/privacidade')
def privacidade():
    """
    Rota para a página de Política de Privacidade.
    
    Exibe informações detalhadas sobre como a empresa coleta,
    usa e protege dados pessoais em conformidade com a LGPD.
    
    Returns:
        Template HTML da política de privacidade
    """
    return render_template(
        'privacidade.html',
        data_atualizacao=datetime.now().strftime('%d de %B de %Y'),
        ano_atual=datetime.now().year
    )


@app.errorhandler(404)
def page_not_found(e):
    """Handler para páginas não encontradas (404)"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handler para erros internos do servidor (500)"""
    return render_template('index.html'), 500


if __name__ == '__main__':
    """
    Executa a aplicação Flask em modo de desenvolvimento.
    
    IMPORTANTE: Em produção, use um servidor WSGI como Gunicorn ou uWSGI
    Exemplo: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    """
    app.run(
        host='0.0.0.0',  # Permite acesso externo (útil para testes em rede local)
        port=5000,
        debug=True  # Desabilitar em produção
    )
