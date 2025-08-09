# routes/about.py
from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from flask_smorest import abort, Blueprint
from datetime import datetime
from app.utilities.utils import *
from app.models.about import About

bp = Blueprint('about', __name__, description='About Implementation Logic', url_prefix='/api')


@bp.route('/about')
class AboutView(MethodView):
    def get(self):
        about = About.fetch_first_record_dict()
        if about:
            return about
        return jsonify({"Message": "No data exists."})

    @jwt_required()
    def post(self):
        about_payload = request.get_json()
        is_exists = About.filter_by_email(email=about_payload.get('Email'))
        current_datetime = datetime.now()
        unavailable_column = []

        if is_exists:
            about_payload.update({'Updated Date': current_datetime})
        else:
            about_payload.update({'Created Date': current_datetime, 'Updated Date': current_datetime})
            new_about_obj = About()

        final_obj = is_exists or new_about_obj
        for key, value in about_payload.items():
            if hasattr(final_obj, key.lower().replace(' ', '_')):
                setattr(final_obj, key.lower().replace(' ', '_'), value)
            else:
                unavailable_column.append(key)

        final_obj.save()

        if unavailable_column:
            message = " except these values {0} as these column doesn't exists".format(unavailable_column)
            return jsonify({"Message": "About inserted/updated successfully" + message})

        return jsonify({'message': 'About inserted/updated successfully'})

    @jwt_required()
    def delete(self):
        try:
            del_payload = request.get_json()
            is_exists = About.filter_by_email(email=del_payload.get('Email'))
            if is_exists:
                is_exists.delete()
                return jsonify({'message': 'About deleted successfully'})
            else:
                return jsonify({'message': "Email: {0} doesn't exists.".format(del_payload.get('Email'))})
        except:
            return jsonify({"Message": "Some exception occured."})
