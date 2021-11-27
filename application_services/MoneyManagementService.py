from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService as d_service

class FriendsResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()
    
    @classmethod
    def get_data_resource_info(cls):
        # db_name, table_name
        return 'aaaaaF21E6156', 'users'
    
    @classmethod
    def get_user_and_address(cls, template):
        db_name, table_name = cls.get_data_resource_info()
        res = d_service.find_by_template(db_name, table_name,
                                          template, None)
        return res