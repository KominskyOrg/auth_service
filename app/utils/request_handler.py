import logging
from flask import jsonify

# Get the logger
logger = logging.getLogger(__name__)


def handle_request(service_function, *args):
    logger.info(f"Handling request for {service_function.__name__}")
    logger.debug(f"Arguments: {args}")
    try:
        response, status_code = service_function(*args)
        logger.debug(f"Response: {response}, Status code: {status_code}")
        return jsonify(response), status_code
    except Exception as e:
        logger.error(f"Error in {service_function.__name__}: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
