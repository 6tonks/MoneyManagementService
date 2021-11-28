from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService as d_service

import uuid
import datetime as dt

class MoneyManagementResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()
    
    @classmethod
    def create_money_account(cls, create_data):

        # time_stamp
        now = dt.datetime.now()

        # Insert initial money for the new player
        ic = create_data
        ic["account_id"] = str(uuid.uuid4())
        ic["money_amount"] = 10000
        ic["coins_amount"] = 0
        ic["last_updated"] = now.strftime("%Y-%m-%d, %H:%M:%S")

        res = MoneyManagementResource.insert_by_template(ic)

        return res

    @classmethod
    def update_money_account(cls, wc, update_data=None):
        
        curr_data = MoneyManagementResource.get_by_template(wc, 1)[0]

        # time_stamp
        now = dt.datetime.now()

        msg = {}

        if update_data["method"] == "addition":
            update_data["money_amount"] += curr_data["money_amount"]
            update_data["last_updated"] = now.strftime("%Y-%m-%d, %H:%M:%S")
            status_code = 200
        elif update_data["method"] == "deduction":
            if update_data["money_amount"] > curr_data["money_amount"]:
                update_data["money_amount"] = curr_data["money_amount"]
                msg['cause_of_error'] = "insufficient_funds"
                status_code = 422
            else:
                update_data["money_amount"] = curr_data["money_amount"] - update_data["money_amount"]
                update_data["last_updated"] = now.strftime("%Y-%m-%d, %H:%M:%S")
                status_code = 200

        del update_data["method"]

        res = MoneyManagementResource.update_by_template(update_data, wc)

        # Output message
        msg['success'] = res

        msg['links'] = {
            'rel': "self",
            'href': f"/money/{wc['user_id']}"
        }

        return msg, status_code
    
    @classmethod
    def get_data_resource_info(cls):
        # db_name, table_name
        return 'moneymgmt', 'buying_power'