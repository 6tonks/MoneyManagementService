from abc import ABC, abstractmethod
from database_services.RDBService import RDBService


class BaseApplicationException(Exception):

    def __init__(self):
        pass


class BaseApplicationResource(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_by_template(cls, template):
        pass

    @classmethod
    @abstractmethod
    def get_links(self, resource_data):
        pass

    @classmethod
    @abstractmethod
    def get_data_resource_info(self):
        pass


class BaseRDBApplicationResource(BaseApplicationResource):

    def __init__(self):
        pass

    @classmethod
    def get_by_template(cls, template):
        db_name, table_name = cls.get_data_resource_info()
        res = RDBService.find_by_template(db_name, table_name,
                                          template, None)
        return res

    @classmethod
    @abstractmethod
    def get_links(self, resource_data):
        # Where clause only supported in get friends
        wc = resource_data.args

        # Pagination
        offs = resource_data.offset
        lim = resource_data.limit
        if not resource_data.limit or (int(lim) > resource_data._default_limit):
            lim = resource_data._default_limit
        
        parent_path = f"{resource_data.path}?"

        if wc: 
            cols = list(wc.keys())
            wc_terms = [c + f"={wc[c]}" for c in cols]
            parsed_wc = ",".join(wc_terms)
            parent_path += f"{parsed_wc}&"
        
        links = []
        if offs:
            self_href = f'{parent_path}limit={lim}&offset={offs}'
            next_href = f'{parent_path}limit={lim}&offset={str(int(offs)+int(lim))}'
            # only have prev when we have offset already
            temp = int(offs)-int(lim)
            if temp > 0:
                prev_href = f'{parent_path}limit={lim}&offset={str(temp)}'
            else: 
                prev_href = f'{parent_path}limit={lim}'
            links.append({'rel': 'prev', 'href': prev_href})
        else:
            self_href = f'{parent_path}limit={lim}'
            next_href = f'{parent_path}limit={lim}&offset={lim}'

        links.append({'rel': 'self', 'href': self_href})
        links.append({'rel': 'next', 'href': next_href})

        flds = resource_data.fields
        if flds:
            for i, link in enumerate(links):
                links[i]['href'] = f"{link['href']}&fields={flds}"
            # Do we need to split to list?
            # flds = flds.split(",")

        return wc, lim, offs, flds, links

    @classmethod
    @abstractmethod
    def get_data_resource_info(self):
        pass
