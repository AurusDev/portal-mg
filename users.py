
import json
import os
from flask_login import UserMixin

# Caminho para arquivo de usuários
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

class User(UserMixin):
    """Classe que representa um usuário autenticado"""
    
    def __init__(self, email, name):
        self.id = email
        self.email = email
        self.name = name
    
    def get_id(self):
        return self.email

def load_users():
    """Carrega lista de usuários do arquivo JSON"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure it returns a dictionary where keys are emails as per usage in app.py
            # Actually, app.py usage: users = load_users(); if email in users: ...
            # AND user_data = next((u for u in users if u['email'] == email), None) 
            # Wait, there is a conflict in usage pattern in my analysis of app.py.
            # Let's check app.py again. 
            # line 83: return data.get('users', []) -> this returns a LIST of dicts.
            # line 97: next((u for u in users if u['email'] == email), None) -> Iterating over LIST.
            # BUT in forgot_password route (step 564): users = load_users(); if email in users: 
            # 'if email in users' works if users is a DICT, not a list.
            # If load_users() returns a list, 'if email in list' checks if the email string is an element of the list (it won't be, elements are dicts).
            # So my previous edit in forgot_password (step 564) assumed users was a dict?
            # Or did I existing code use a dict?
            # Existing code: line 83 return data.get('users', []) which returns a list.
            # So 'if email in users' in forgot_password is WRONG if users is a list.
            # I must fix this logic in users.py OR consistent usage.
            
            # Use dictionary for easier lookups?
            # The existing file structure seems to possess a list under 'users' key.
            # Let's keep returning the list for compatibility with existing registration logic if any?
            # Registration logic usually appends to list.
            # Let's check Register route usage (it wasn't shown in recent view).
            
            # I will strictly copy the logic from app.py first to be safe, but I suspect 'forgot_password' logic I added is buggy.
            return data.get('users', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users_list(users_list):
    """Salva lista de usuários no arquivo JSON"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': users_list}, f, ensure_ascii=False, indent=2)

def save_users(users_data):
    """
    Overloaded/Smart save. If users_data is a dict (email -> data), convert to list.
    If it is a list, save as is.
    Wait, let's look at how I used it in reset_password:
    users = load_users() (returns list)
    if email in users: (BUG: checking email in list of dicts)
       users[email]['password'] = ... (BUG: list indices must be integers)
    
    So my forgot/reset password logic assumed 'load_users' returns a DICT.
    But the existing 'load_users' in app.py returns a LIST.
    
    I MUST standardize to a Dictionary for O(1) lookups and easier management, 
    OR fix my new code to work with Lists.
    
    Given I am refactoring, I should change load_users to return a Dict {email: user_data}
    BUT I must ensure I don't break existing 'User' loader or Register route.
    
    Let's check 'load_user' in app.py (line 68):
    users = load_users()
    user_data = next((u for u in users if u['email'] == email), None)
    This expects a LIST.
    
    DECISION:
    I will keep `load_users()` returning a LIST (to not break Login/Register if I don't see them).
    AND I will implement `load_users_as_dict()` or just handle the conversion in the new helper methods.
    
    ACTUALLY, to fix the logic I added in reset_password/forgot_password:
    I will update `users.py` to include `get_user_by_email` and `update_user_password`.
    This encapsulates the logic and hides the list vs dict storage detail.
    
    Let's defined helper functions:
    - get_all_users() -> returns list
    - get_user(email) -> returns dict or None
    - save_user(email, data) -> updates/appends
    
    BUT `app.py` imported `load_users` and `save_users`.
    So I should probably stick to the names but fix the implementation or usage.
    
    Let's stick to the current implementation of `load_users` (returning list) 
    and fix the logic in `forgot_password` and `reset_password` inside `app.py` to use correct list operations,
    OR provide better functions in `users.py` and import those.
    
    Better functions is the way.
    """
    pass

# Actual implementation for users.py
def get_all_users(): 
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('users', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_users(): # Keep name for compatibility
    return get_all_users()

def save_users(users_list):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': users_list}, f, ensure_ascii=False, indent=2)

def get_user_by_email(email):
    users = load_users()
    return next((u for u in users if u['email'] == email), None)

def update_user_password(email, new_password_hash):
    users = load_users()
    for user in users:
        if user['email'] == email:
            user['password_hash'] = new_password_hash
            save_users(users)
            return True
    return False

