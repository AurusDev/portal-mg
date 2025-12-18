from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class System(db.Model):
    """Sistemas disponíveis na plataforma"""
    __tablename__ = 'systems'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(20), default='main') # 'main' or 'automation'
    url = db.Column(db.String(200), nullable=False)
    icon_class = db.Column(db.String(50)) # CSS class or filename
    is_public = db.Column(db.Boolean, default=False)
    
    # Relationships
    access_grants = db.relationship('UserSystemAccess', backref='system', lazy=True)

class User(UserMixin, db.Model):
    """Usuário autenticado"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user') # 'admin', 'manager', 'user'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('UserSystemAccess', foreign_keys='UserSystemAccess.user_id', backref='user', lazy=True)
    
    def has_access(self, system_id):
        """Verifica se o usuário tem acesso a um sistema específico"""
        if self.role == 'admin':
            return True
            
        # Check explicit permission
        # Also check if system is public (needs a helper or join, but keeping it simple)
        if hasattr(self, '_cached_permissions'):
             return system_id in self._cached_permissions
             
        # Allow checking public systems if we had a way to check 'system.is_public' cheaply here.
        # But for now, we rely on the controller to filter.
        
        permission = UserSystemAccess.query.filter_by(
            user_id=self.id, 
            system_id=system_id
        ).first()
        return permission is not None

class UserSystemAccess(db.Model):
    """Tabela de Ligação (ACL)"""
    __tablename__ = 'user_system_access'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    system_id = db.Column(db.String(50), db.ForeignKey('systems.id'), primary_key=True)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Admin ID
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    """Trilha de Auditoria"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Who did it
    target_id = db.Column(db.String(50)) # User ID or System ID affected (stored as string for flexibility)
    action = db.Column(db.String(50), nullable=False) # GRANT_ACCESS, REVOKE_ACCESS, etc.
    meta_info = db.Column(db.JSON) # Extra details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
