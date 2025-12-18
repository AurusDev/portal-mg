"""
Portal Corporativo Mendonça Galvão Contadores Associados
=========================================================

Aplicação Flask que centraliza o acesso aos sistemas internos da empresa.
Implementa RBAC e ACL para gestão de acessos.

Autor: Núcleo Digital MG
Data: 2025-12-18
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

# Import Models and DB
from models import db, User, System, UserSystemAccess, AuditLog
from admin_routes import admin_bp

# Import Employee Validation
from employees import is_valid_email_domain, is_employee_registered

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar aplicação Flask
app = Flask(__name__)

# Configurações
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database Config (SQLite)
# Database Config (SQLite)
basedir = os.path.abspath(os.path.dirname(__file__))
# Default to SQLite with absolute path if DATABASE_URL not set
default_db_url = 'sqlite:///' + os.path.join(basedir, 'portal_mg.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', default_db_url)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

# Register Blueprints
app.register_blueprint(admin_bp)

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

if not app.config['MAIL_USERNAME']:
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

@login_manager.user_loader
def load_user(user_id):
    """Carrega um usuário baseado no ID (PK)"""
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    """
    Rota principal. Renderiza apenas sistemas permitidos.
    """
    # Buscar todos os sistemas
    all_systems = System.query.all()
    
    # Filtrar sistemas permitidos
    allowed_systems = []
    for sistema in all_systems:
        # Se for publico OU usuário tem permissão
        if sistema.is_public or current_user.has_access(sistema.id):
            # Converter para dict para o template se necessário, ou usar objeto direto
            # O template espera objeto com .titulo, .descricao, etc.
            # O model usa .name, .description.
            # Vou adaptar aqui para manter compatibilidade com template index.html
            
            # Mapeamento do Model -> Dict esperado pelo template antigo
            sys_dict = {
                'id': sistema.id,
                'titulo': sistema.name,
                'descricao': sistema.description,
                'url': sistema.url,
                'icone': sistema.icon_class,
                'cta': 'Acessar', # Default CTA
                'category': sistema.category
            }
            if 'portal' in sistema.id: sys_dict['cta'] = 'Acessar Portal'
            elif 'comissao' in sistema.id: sys_dict['cta'] = 'Calcular Comissão'
            elif 'ponto' in sistema.id: sys_dict['cta'] = 'Processar Ponto'
            
            allowed_systems.append(sys_dict)
            
    # Separar para compatibilidade com abas (index.html filtrava por ID ou lógica?)
    # O index.html original itera sobre 'sistemas' para a aba Principal.
    # E tinha "Placeholder" para automações.
    # Agora vamos passar TUDO e o filtro visual deve ser feito se quisermos separar abas.
    # O index.html usa 'sistemas' e 'automacoes' (hardcoded?).
    # O index.html original iterava `{% for sistema in sistemas %}` na aba 'sistemas-principais'.
    # E na aba 'automacoes' tinha placeholder.
    
    # Preciso atualizar index.html para iterar corretamente se eu quiser que automações apareçam na aba certa.
    # Mas o user pediu para não quebrar UI.
    # Vou passar 'sistemas' filtrado.
    
    # Membros da Equipe (Estático por enquanto)
    team_members = [
        {'nome': 'Tiago Nunes', 'foto': 'tiago-nunes.jpg'},
        {'nome': 'Guilherme Almeida', 'foto': 'guilherme-almeida.jpg'},
        {'nome': 'Eduardo Melo', 'foto': 'eduardo-melo.jpg'},
        {'nome': 'Arthur Monteiro', 'foto': 'team-member.jpg'}
    ]
    
    return render_template(
        'index.html',
        sistemas=allowed_systems,
        team_members=team_members,
        current_user=current_user,
        ano_atual=datetime.now().year
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        # Auth via DB
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            if not user.is_active:
                flash('Conta desativada.', 'error')
                return render_template('login.html')
                
            login_user(user)
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
            
        flash('Email ou senha incorretos.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([name, email, password, confirm_password]):
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('register.html')
        
        if not is_valid_email_domain(email):
            flash('Email deve ser do domínio @mendoncagalvao.com.br', 'error')
            return render_template('register.html')
            
        if not is_employee_registered(email):
            flash('Email não encontrado na base de funcionários.', 'error')
            return render_template('register.html')
            
        if len(password) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'error')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'error')
            return redirect(url_for('login'))
            
        # Create User
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            role='user', # Default role
            created_at=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Grant Public Systems
        public_systems = System.query.filter_by(is_public=True).all()
        for sys in public_systems:
            access = UserSystemAccess(user_id=new_user.id, system_id=sys.id)
            db.session.add(access)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email').lower().strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = serializer.dumps(email, salt='recover-key')
            send_reset_email(email, token)
            flash('Link de redefinição enviado.', 'info')
        else:
            flash('Se o email existir, você receberá o link.', 'info')
            
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    try:
        email = serializer.loads(token, salt='recover-key', max_age=3600)
    except:
        flash('Link inválido ou expirado.', 'error')
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('reset_password', token=token))
            
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            flash('Senha redefinida com sucesso.', 'success')
            return redirect(url_for('login'))
        else:
             flash('Usuário não encontrado.', 'error')

    return render_template('reset_password.html', token=token)

def send_reset_email(user_email, token):
    msg = Message('Redefinição de Senha', sender='noreply@mgcontadores.com.br', recipients=[user_email])
    reset_url = url_for('reset_password', token=token, _external=True)
    msg.html = render_template('email/reset_password.html', reset_url=reset_url, year=datetime.now().year)
    if app.config.get('MAIL_SUPPRESS_SEND'):
        print(f"RESET LINK: {reset_url}")
    mail.send(msg)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/privacidade')
def privacidade():
    return render_template('privacidade.html', data_atualizacao=datetime.now().strftime('%d/%m/%Y'), ano_atual=datetime.now().year)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('index.html'), 500

if __name__ == '__main__':
    # Auto-init DB for dev
    db_file = os.path.join(basedir, 'portal_mg.db')
    if not os.path.exists(db_file):
        print("Inicializando Banco de Dados...")
        from init_db import init_db
        init_db()
        
    app.run(host='0.0.0.0', port=5000, debug=True)
