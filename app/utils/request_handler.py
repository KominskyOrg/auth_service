import logging
from flask import jsonify


def handle_request(service_function, *args):
    try:
        response, status_code = service_function(*args)
        return jsonify(response), status_code
    except Exception as e:
        logging.error(f"Error in {service_function.__name__}: {e}")
        return jsonify({"error": "Internal server error"}), 500
