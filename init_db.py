from app import app
from models import db, User, System, UserSystemAccess
from users import load_users as load_legacy_users
from datetime import datetime
import os

def init_db():
    """Inicializa o banco de dados e migra dados legados"""
    
    # Check if DB needs initialization
    with app.app_context():
        # Debug paths
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'portal_mg.db')
        print(f"DEBUG: CWD: {os.getcwd()}")
        print(f"DEBUG: Basedir: {basedir}")
        print(f"DEBUG: Internal DB Path should be: {db_path}")
        print(f"DEBUG: App Config URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        import sqlite3
        print(f"DEBUG: SQLite Version: {sqlite3.sqlite_version}")

        
        # 1. Try generic create_all
        try:
            db.create_all()
            print("db.create_all() executed successfully.")
        except Exception as e:
            print(f"ERROR in db.create_all(): {e}")

        # 2. Manual Verification & Fallback
        from sqlalchemy import inspect, text
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Tables found after create_all: {tables}")
            
            if 'users' not in tables:
                print("WARNING: 'users' table missing. Attempting manual SQL creation...")
                # Fallback: Create specifically the users table via raw SQL if Alchemy failed
                with db.engine.connect() as conn:
                    conn.execute(text('''
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            email VARCHAR(120) NOT NULL UNIQUE,
                            name VARCHAR(100) NOT NULL,
                            password_hash VARCHAR(256),
                            role VARCHAR(20) DEFAULT 'user',
                            is_active BOOLEAN DEFAULT 1,
                            created_at DATETIME
                        )
                    '''))
                    conn.execute(text('''
                        CREATE TABLE IF NOT EXISTS systems (
                            id VARCHAR(50) PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            description VARCHAR(200),
                            category VARCHAR(20) DEFAULT 'main',
                            url VARCHAR(200) NOT NULL,
                            icon_class VARCHAR(50),
                            is_public BOOLEAN DEFAULT 0
                        )
                    '''))
                    # Also Access Table
                    conn.execute(text('''
                        CREATE TABLE IF NOT EXISTS user_system_access (
                            user_id INTEGER,
                            system_id VARCHAR(50),
                            granted_by INTEGER,
                            granted_at DATETIME,
                            PRIMARY KEY (user_id, system_id),
                            FOREIGN KEY(user_id) REFERENCES users(id),
                            FOREIGN KEY(system_id) REFERENCES systems(id)
                        )
                    '''))
                    conn.commit()
                print("Manual SQL creation executed.")
        except Exception as e:
            print(f"CRITICAL ERROR inspecting/creating tables manually: {e}")


        
        # 1. Seed Systems
        systems_data = [
            {
                'id': 'portal-colaborador',
                'name': 'Portal do Colaborador',
                'description': 'Gerencie suas informações pessoais, contracheques, férias e benefícios de forma rápida e segura.',
                'url': 'https://portalcolabmg.lovable.app/login',
                'icon_class': 'icon-portal.png',
                'category': 'main',
                'is_public': True # Everyone should see this? Let's say yes for now, or explicit grant. Default: True for Portal.
            },
            {
                'id': 'sistema-comissao',
                'name': 'Sistema de Cálculo de Comissão',
                'description': 'Calcule suas comissões de forma automática e transparente, com relatórios detalhados.',
                'url': 'https://calculadp.lovable.app/',
                'icon_class': 'icon-comissao.png',
                'category': 'main',
                'is_public': False
            },
            {
                'id': 'ponto-eletronico',
                'name': 'Processamento Inteligente de Ponto Eletrônico',
                'description': 'Faça upload dos espelhos de ponto (PDF ou Imagem). O sistema identifica automaticamente faltas (integrais e parciais), horas extras e adicional noturno.',
                'url': 'https://ai.studio/apps/drive/1-7xvcz9OLnLck0vtStQp4u375oKg4MyV?fullscreenApplet=true',
                'icon_class': 'icon-ponto.png',
                'category': 'automation',
                'is_public': False
            },
            {
                'id': 'adiantamento-salarial',
                'name': 'Cálculo Automático de Adiantamento',
                'description': 'Importe o PDF da folha de pagamento para iniciar o processamento automático de adiantamento salarial mensal.',
                'url': 'https://ai.studio/apps/drive/14NzWtRjoDQhHhwxaDIeZisxTAzIZDkvq?fullscreenApplet=true',
                'icon_class': 'icon-adiantamento.png',
                'category': 'automation',
                'is_public': False
            },
            {
                'id': 'grid-x',
                'name': 'GridX',
                'description': 'Seu conversor inteligente para Windows. Transforme dados em insights de forma rápida, simples e eficiente.',
                'url': 'https://gridx.lovable.app/',
                'icon_class': 'icon-gridx.png',
                'category': 'main',
                'is_public': True
            },
            {
                'id': 'arca-mg',
                'name': 'Arca MG',
                'description': 'Analisador de Documentos. Envie seus arquivos Excel e PDF para análise inteligente e correlação de dados.',
                'url': 'https://arcamg.lovable.app/',
                'icon_class': 'icon-arca.png',
                'category': 'main',
                'is_public': True
            },
            {
                'id': 'aeronord-convocacoes',
                'name': 'Aeronord - Convocações & Recibos',
                'description': 'Sistema interno para cálculo automático de convocações e geração de recibos da Aeronord, com interface dark premium, apuração mensal consolidada',
                'url': 'https://aerocv.lovable.app/convenios',
                'icon_class': 'icon-aeronord.png',
                'category': 'main',
                'is_public': True
            },
            {
                'id': 'calculadora-rescisao',
                'name': 'Calculadora de Rescisão',
                'description': 'Ferramenta automática para cálculo de rescisão trabalhista com interface intuitiva e cálculos precisos',
                'url': 'https://calculadoramg.lovable.app/',
                'icon_class': 'icon-rescisao.png',
                'category': 'main',
                'is_public': True
            }
        ]
        
        for sys_data in systems_data:
            existing = System.query.get(sys_data['id'])
            if not existing:
                print(f"Criando sistema: {sys_data['name']}")
                new_sys = System(
                    id=sys_data['id'],
                    name=sys_data['name'],
                    description=sys_data['description'],
                    url=sys_data['url'],
                    icon_class=sys_data['icon_class'],
                    category=sys_data['category'],
                    is_public=sys_data.get('is_public', False)
                )
                db.session.add(new_sys)
        
        db.session.commit()
        
        # 2. Migrate Users from JSON
        legacy_users = load_legacy_users() # Returns list of dicts
        
        # Admin Emails
        ADMIN_EMAILS = ["admin@mendoncagalvao.com.br", "arthur.monteiro@mendoncagalvao.com.br"] # Explicitly add Arthur
        
        for u_data in legacy_users:
            email = u_data['email']
            existing_user = User.query.filter_by(email=email).first()
            
            # Determine correct role
            target_role = 'admin' if email in ADMIN_EMAILS else 'user'
            
            if existing_user:
                 # Check if we need to promote existing user
                 if existing_user.role != target_role and target_role == 'admin':
                     print(f"Promovendo usuário existente para admin: {email}")
                     existing_user.role = 'admin'
                     db.session.add(existing_user) # Mark for update

            if not existing_user:
                print(f"Migrando usuário: {email}")
                
                new_user = User(
                    email=email,
                    name=u_data['name'],
                    password_hash=u_data.get('password_hash', ''),
                    role=target_role,
                    is_active=True,
                    created_at=datetime.fromisoformat(u_data['created_at']) if 'created_at' in u_data else datetime.utcnow()
                )
                db.session.add(new_user)
                db.session.flush() # Get ID
                
                # Grant default access to public systems?
                # Or emulate old behavior: everyone had access to everything in the hardcoded list?
                # The prompt says: "Já existe uma central/hub com cards... Quero uma área admin para definir".
                # Implication: Currently everyone sees everything.
                # Migration strategy: Grant access to ALL systems for EXISTING users to avoid breakage.
                
                all_systems = System.query.all()
                for system in all_systems:
                     access = UserSystemAccess(user_id=new_user.id, system_id=system.id)
                     db.session.add(access)
            
        db.session.commit()
        print("Migração concluída.")

if __name__ == '__main__':
    init_db()
