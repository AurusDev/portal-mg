from app import app
from models import db, User, System, UserSystemAccess
from users import load_users as load_legacy_users
from datetime import datetime
import os

def init_db():
    """Inicializa o banco de dados e migra dados legados"""
    
    # Check if DB needs initialization (simple check: any users?)
    with app.app_context():
        db.create_all()
        
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
        
        # Default Admin Email (for bootstrapping)
        ADMIN_EMAIL = "admin@mendoncagalvao.com.br" # Replace with real one if known, or auto-detect
        
        for u_data in legacy_users:
            email = u_data['email']
            existing_user = User.query.filter_by(email=email).first()
            
            if not existing_user:
                print(f"Migrando usuário: {email}")
                role = 'admin' if email == ADMIN_EMAIL else 'user'
                
                new_user = User(
                    email=email,
                    name=u_data['name'],
                    password_hash=u_data.get('password_hash', ''),
                    role=role,
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
