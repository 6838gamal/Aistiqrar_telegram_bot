users = {}

def set_user(user_id, lang="ar"):
    users[user_id] = {
        "lang": lang,
        "sessions": 0
    }

def get_user(user_id):
    return users.get(user_id, {"lang": "ar", "sessions": 0})
