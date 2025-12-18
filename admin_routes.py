from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, System, UserSystemAccess, AuditLog
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'manager']:
            flash('Acesso não autorizado.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Painel Principal do Admin"""
    stats = {
        'users_count': User.query.count(),
        'systems_count': System.query.count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }
    
    # Recent logs
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, logs=logs)

@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """Listagem de usuários"""
    search = request.args.get('search', '')
    query = User.query
    
    if search:
        query = query.filter(User.name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%'))
        
    users = query.order_by(User.name).all()
    return render_template('admin/users_list.html', users=users, search=search)

@admin_bp.route('/users/<int:user_id>/permissions', methods=['GET', 'POST'])
@login_required
@admin_required
def user_permissions(user_id):
    """Gerenciar permissões de um usuário"""
    target_user = User.query.get_or_404(user_id)
    
    # Prevent editing self role/permissions if strict security needed, 
    # but for now let's just log it. 
    # Or restrict Managers from editing Admins.
    if current_user.role == 'manager' and target_user.role == 'admin':
        flash('Gestores não podem editar Administradores.', 'error')
        return redirect(url_for('admin.list_users'))

    if request.method == 'POST':
        # Get list of allowed system IDs
        allowed_systems = request.form.getlist('systems')
        
        # 1. Update Role if present
        new_role = request.form.get('role')
        if new_role and new_role in ['user', 'manager', 'admin']:
            # Only admin can change roles
            if current_user.role == 'admin':
                if target_user.role != new_role:
                    target_user.role = new_role
                    # Audit Role Change
                    log = AuditLog(
                        actor_id=current_user.id,
                        target_id=str(target_user.id),
                        action='UPDATE_ROLE',
                        meta_info={'new_role': new_role}
                    )
                    db.session.add(log)
        
        # 2. Update Systems Access (Sync approach)
        # Strategy: Delete all existing and re-insert checks. 
        # Or better: compare sets to log efficiently.
        
        current_accesses = {a.system_id for a in target_user.permissions}
        new_accesses = set(allowed_systems)
        
        to_add = new_accesses - current_accesses
        to_remove = current_accesses - new_accesses
        
        # Add Grants
        for sys_id in to_add:
            access = UserSystemAccess(user_id=target_user.id, system_id=sys_id, granted_by=current_user.id)
            db.session.add(access)
            # Log
            log = AuditLog(
                actor_id=current_user.id,
                target_id=f"User:{target_user.id}",
                action='GRANT_ACCESS',
                meta_info={'system': sys_id}
            )
            db.session.add(log)
            
        # Revokes
        if to_remove:
            UserSystemAccess.query.filter(
                UserSystemAccess.user_id == target_user.id,
                UserSystemAccess.system_id.in_(to_remove)
            ).delete(synchronize_session=False)
            
            for sys_id in to_remove:
                log = AuditLog(
                    actor_id=current_user.id,
                    target_id=f"User:{target_user.id}",
                    action='REVOKE_ACCESS',
                    meta_info={'system': sys_id}
                )
                db.session.add(log)
        
        try:
            db.session.commit()
            flash(f'Permissões de {target_user.name} atualizadas.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'error')
            
        return redirect(url_for('admin.user_permissions', user_id=user_id))

    # GET
    systems = System.query.all()
    # Group systems by category
    systems_by_category = {}
    for s in systems:
        cat = s.category or 'Outros'
        if cat not in systems_by_category:
            systems_by_category[cat] = []
        systems_by_category[cat].append(s)

    # Get user allowed system IDs for checkboxes
    user_system_ids = {p.system_id for p in target_user.permissions}
    
    return render_template(
        'admin/user_edit.html', 
        user=target_user, 
        systems_by_category=systems_by_category,
        user_system_ids=user_system_ids
    )
