from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException

def handle_http_exception(e):
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": e.description,
            "code": e.code,
            "status": "error"
        }
        return jsonify(response), e.code
    return render_template('errors/error.html', error=e), e.code

def handle_404(e):
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": "Resource not found",
            "code": 404,
            "status": "error",
            "path": request.path
        }
        return jsonify(response), 404
    return render_template('errors/404.html', path=request.path), 404

def handle_500(e):
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": "Internal Server Error",
            "code": 500,
            "status": "error"
        }
        return jsonify(response), 500
    return render_template('errors/500.html'), 500

def register_error_handlers(app):
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)