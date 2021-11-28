import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
           **db_info,
            autocommit=True
        )
        return db_connection

    @classmethod
    def _run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
            column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def _get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k,v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " +  " AND ".join(terms)


        return clause, args

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, limit=10, offset=None, field_list=None):

        # Get the where clause
        wc, args = RDBService._get_where_clause_args(template)

        # Add field list selector
        if field_list:
            sql = f"select {field_list} from {db_schema}.{table_name} {wc} limit {limit}"
        else:
            sql = f"select * from {db_schema}.{table_name} {wc} limit {limit}"
        
        # Add offset
        if offset:
            sql += f" offset {offset}"

        # Run the query
        res = RDBService._run_sql(sql, args, fetch=True)

        return res

    @classmethod
    def _post_insert_clause_args(cls, template):
        
        cols = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k,v in template.items():
                # cols.append("`"+k+"`")
                cols.append(k)
                args.append(v)

            col_formatted = " (" + ", ".join(cols) + ") "
            val_formatted = " (" + ", ".join(["%s"]*len(cols)) + ") "
            clause = "{}values{}".format(col_formatted, val_formatted)

        return clause, args

    @classmethod
    def create_resource(cls, db_schema, table_name, create_data):
        
        # generate SQL query
        insert_clause, args = RDBService._post_insert_clause_args(create_data)
        sql = f"insert into {db_schema}.{table_name} {insert_clause}"

        # Run the query
        res = RDBService._run_sql(sql, args)
        
        return res
    
    @classmethod
    def _get_update_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k,v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " set " +  ", ".join(terms)


        return clause, args
    
    @classmethod
    def update_resource(cls, db_schema, table_name, update_data, where_clause):
        
        # get where clause
        wc, wc_args = RDBService._get_where_clause_args(where_clause)
        
        # Get the update data clause
        uc, uc_args = RDBService._get_update_clause_args(update_data)
        
        # Generate query
        sql = f"update {db_schema}.{table_name} {uc} {wc}"
        
        # combine args
        args = uc_args + wc_args
        
        # Run the query
        res = RDBService._run_sql(sql, args)

        return res
    
    @classmethod
    def delete_resource(cls, db_schema, table_name, delete_data):
        
        # Get the where clause
        wc, args = RDBService._get_where_clause_args(delete_data)
        sql = f"delete from {db_schema}.{table_name} {wc}"
        
        # Run the query
        res = RDBService._run_sql(sql, args)

        return res