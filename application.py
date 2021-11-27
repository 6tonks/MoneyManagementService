from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging
from datetime import datetime

import utils.rest_utils as rest_utils

from application_services.MoneyManagementService import MoneyManagementResource
from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

# DFF TODO A real service would have more robust health check methods.
# This path simply echoes to check that the app is working.
# The path is /health and the only method is GETs
@app.route("/health", methods=["GET"])
def health_check():
    now = datetime.now()
    rsp_data = {"status": "healthy", "time": now.strftime("%Y-%m-%d, %H:%M:%S")}
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="app/json")
    return rsp


# TODO Remove later. Solely for explanatory purposes.
# The method take any REST request, and produces a response indicating what
# the parameters, headers, etc. are. This is simply for education purposes.
#
@app.route("/api/demo/<parameter1>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/api/demo/", methods=["GET", "POST", "PUT", "DELETE"])
def demo(parameter1=None):
    """
    Returns a JSON object containing a description of the received request.

    :param parameter1: The first path parameter.
    :return: JSON document containing information about the request.
    """

    # DFF TODO -- We should wrap with an exception pattern.
    #

    # Mostly for isolation. The rest of the method is isolated from the specifics of Flask.
    inputs = rest_utils.RESTContext(request, {"parameter1": parameter1})

    # DFF TODO -- We should replace with logging.
    r_json = inputs.to_json()
    msg = {
        "/demo received the following inputs": r_json
    }
    print("/api/demo/<parameter> received/returned:\n", msg)

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp



@app.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/gabrielle')
def hello_gabrielle():
    return '<u>Yay! Gabrielle is here!!!!!!!</u>'


@app.route('/users', methods=['GET', 'POST'])
def user_collection():
    """
    1. HTTP GET return all users.
    2. HTTP POST with body --> create a user, i.e --> database.
    :return:
    """
    # res = MoneyManagementResource.get_by_template(None)
    # rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    # return rsp
    inputs = rest_utils.RESTContext(request)

    # DFF TODO -- We should replace with logging.
    r_json = inputs.to_json()
    msg = {
        "/demo received the following inputs": r_json
    }

    # if r_json['method']=="GET":
    wc, lim, offs, flds, links = MoneyManagementResource.get_links(inputs)

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp

@app.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_user(user_id):
    """
    1. Get a specific one by ID.
    2. Update body and update.
    3. Delete would ID and delete it.
    :param user_id:
    :return:
    """
    pass

@app.route('/<db_schema>/<table_name>/<column_name>/<prefix>')
def get_by_prefix(db_schema, table_name, column_name, prefix):
    res = RDBService.get_by_prefix(db_schema, table_name, column_name, prefix)
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
