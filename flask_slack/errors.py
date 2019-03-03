from flask import jsonify


def forbidden(message):
    return jsonify({'error': 'forbidden', 'message': message}), 403
