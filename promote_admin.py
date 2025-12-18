from app import app
from models import db, User

def promote_user(email):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = 'admin'
            db.session.commit()
            print(f"Sucesso: Usuário {email} agora é ADMIN.")
        else:
            print(f"Erro: Usuário {email} não encontrado.")

if __name__ == "__main__":
    # Promote the user visible in the screenshot
    promote_user('arthur.monteiro@mendoncagalvao.com.br')
    
    # Also ensure the default admin is set if needed, but priority is the user's active account
