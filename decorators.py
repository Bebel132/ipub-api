from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not get_jwt().get("is_admin"):
            return jsonify({"error": "Acesso negado"}), 403

        return fn(*args, **kwargs)

    return wrapper


def admin_or_owner(param="id"):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()

            if claims.get("is_admin"):
                return fn(*args, **kwargs)

            if str(get_jwt_identity()) == str(kwargs[param]):
                return fn(*args, **kwargs)

            return jsonify({"error": "Acesso negado"}), 403

        return wrapper

    return decorator