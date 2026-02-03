from backend.storage import load_users, save_users

def login_user(email, password):
    users = load_users()
    if email in users and users[email]["password"] == password:
        return True, users[email]
    return False, None

def register_user(name, email, password):
    users = load_users()
    if email in users:
        return False
    users[email] = {"name": name, "password": password}
    save_users(users)
    return True
