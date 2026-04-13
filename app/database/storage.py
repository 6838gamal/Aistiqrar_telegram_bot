from app.database.db import upsert_user, get_user as db_get_user

def set_user(user_id, lang="ar", name="", username="", referred_by=None):
    upsert_user(user_id, name=name, username=username, lang=lang, referred_by=referred_by)

def get_user(user_id):
    return db_get_user(user_id)
