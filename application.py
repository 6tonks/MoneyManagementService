from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging
from datetime import datetime

import utils.rest_utils as rest_utils

from application_services.MoneyManagementService import MoneyManagementResource

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


@app.route('/money', methods=['GET', 'POST'])
def money_collection():
    """
    1. HTTP GET return all users.
    2. HTTP POST with body --> create a user, i.e --> database.
    :return:
    """
    inputs = rest_utils.RESTContext(request)

    # log request
    rest_utils.log_request("money_collection", inputs)

    try:

        if inputs.method=="GET":
            wc, lim, offs, flds, links = MoneyManagementResource.get_links(inputs)
            res = MoneyManagementResource.get_by_template(wc, lim, offs, flds)

            # Output message
            msg = {}
            msg['money_accounts'] = res
            
            # links
            msg['links'] = links

            # remove next if empty result list or result less than limit
            if not res or len(res)<int(lim):
                msg['links'] = msg['links'][:-1]
            
            # Response 200 for success
            rsp = Response(json.dumps(msg), status=200, content_type="application/json")

        elif inputs.method=="POST":
            ic = inputs.data
            res = MoneyManagementResource.create_money_account(ic)
            
            # Output message
            msg = {}
            msg['success'] = res

            msg['links'] = {
                'rel': "self",
                'href': f"/money/{ic['user_id']}"
            }

            # Response 201 for POST -- CREATED
            rsp = Response(json.dumps(msg), status=201, content_type="application/json")

        else:
            # Response 501 for unimplemented method
            rsp = Response("NOT IMPLEMENTED", status=501, content_type="text/plain")

    except Exception as e:
        # HTTP status code.
        logging.error("{}, e = {}".format(inputs.path, e))
        rsp = Response("INTERNAL ERROR", status=500, content_type="text/plain")

    return rsp

@app.route('/money/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def specific_money_collection(user_id):
    """
    1. Get a specific one by ID.
    2. Update body and update.
    3. Delete would ID and delete it.
    :param user_id:
    :return:
    """
    inputs = rest_utils.RESTContext(request)

    # log request
    rest_utils.log_request("specific_money_collection", inputs)

    try:
        
        if inputs.method=="GET":
            # only get selected variables
            wc, _, _, flds, _ = MoneyManagementResource.get_links(inputs)
            
            # ensure user_id is in the where clause
            wc["user_id"] = user_id
            res = MoneyManagementResource.get_by_template(wc, 1, field_list=flds)
            
            # Output message
            msg = {}
            msg['money_account'] = res[0]
            
            # links
            msg['links'] = {
                'rel': "self",
                'href': f"/money/{wc['user_id']}"
            }
            
            # Response 200 for success
            rsp = Response(json.dumps(msg), status=200, content_type="application/json")

        elif inputs.method=="PUT":
            # user_id as where clause
            wc = {"user_id": user_id}

            # add or reduce money
            update_data = inputs.data
            # AWS Step Function can only send string request
            update_data["money_amount"] = float(update_data["money_amount"])

            res_msg, status_code = MoneyManagementResource.update_money_account(wc, update_data)
            
            # Response 200 for success, 422 for bad data
            rsp = Response(json.dumps(res_msg), status=status_code, content_type="application/json")

        elif inputs.method=="DELETE":
            # user_id as where clause
            wc = {"user_id": user_id}

            res = MoneyManagementResource.delete_by_template(wc)

            msg = {}
            msg['success'] = res

            # Response 204 for DELETE
            rsp = Response(json.dumps(msg), status=204, content_type="application/json")

        else:
            # Response 501 for unimplemented method
            rsp = Response("NOT IMPLEMENTED", status=501)

    except Exception as e:
        # HTTP status code.
        logging.error("{}, e = {}".format(inputs.path, e))
        rsp = Response("INTERNAL ERROR", status=500, content_type="text/plain")

    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=False)
