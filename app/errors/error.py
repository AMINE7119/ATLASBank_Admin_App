from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException, Forbidden, Unauthorized, NotFound
from app.logger.app_logging import setup_logging

logger = setup_logging()

def handle_http_exception(e):
    
    logger.error(f"HTTP Exception: {e.code} - {e.description} - Path: {request.path}")
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": e.description,
            "code": e.code,
            "status": "error",
            "path": request.path
        }
        return jsonify(response), e.code
    return render_template('errors/error.html', error=e), e.code

def handle_404(e):
    
    logger.warning(f"404 Error for path: {request.path}")
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
    
    logger.error(f"500 Error: {str(e)} - Path: {request.path}")
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": "Internal Server Error",
            "code": 500,
            "status": "error",
            "path": request.path
        }
        return jsonify(response), 500
    return render_template('errors/500.html'), 500

def handle_403(e):
    
    logger.warning(f"403 Forbidden error for path: {request.path}")
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": "Forbidden - Access denied",
            "code": 403,
            "status": "error",
            "path": request.path
        }
        return jsonify(response), 403
    return render_template('errors/403.html', error=e), 403

def handle_401(e):
    
    logger.warning(f"401 Unauthorized error for path: {request.path}")
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        response = {
            "error": "Unauthorized - Authentication required",
            "code": 401,
            "status": "error",
            "path": request.path
        }
        return jsonify(response), 401
    return render_template('errors/401.html', error=e), 401

def register_error_handlers(app):
    
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(500, handle_500)
    app.register_error_handler(403, handle_403)
    app.register_error_handler(401, handle_401)

    
    return app