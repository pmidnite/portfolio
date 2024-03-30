from flask_jwt_extended import create_access_token
from flask import Blueprint, request, jsonify

bp = Blueprint("auth", __name__, url_prefix="/get_token")

@bp.route("", methods=["POST"])
def generate_token():
    try:
        userkey = request.json.get("username")
        passkey = request.json.get("password")
        # This can be matched with DB user details value
        if userkey == "test" and passkey == "Password":
            access_token = create_access_token(identity={"username": userkey,
                                                         "password": passkey})
            return jsonify(access_token=access_token), 200
    except:
        return jsonify({"Message": "Invalid credentials."}), 401
