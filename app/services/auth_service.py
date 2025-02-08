from app.dal.admin_dao import get_admin_by_username
def authenticate_admin(username, password):
    admin = get_admin_by_username(username)
    if admin and admin.password == password:
        return admin
    return None