import os

from .db_config import db_connect_info

# This is a bad place for this import
import pymysql

def get_db_info():
    """
    This is crappy code.

    :return: A dictionary with connect info for MySQL
    """
    db_host = os.environ.get("DBHOST", None)
    db_user = os.environ.get("DBUSER", None)
    db_password = os.environ.get("DBPASSWORD", None)

    if db_host is not None:
        db_info = {
            "host": db_host,
            "user": db_user,
            "password": db_password,
            "cursorclass": pymysql.cursors.DictCursor
        }
    else:
        db_info = {
            "host": db_connect_info["DBHOST"],
            "user": db_connect_info["DBUSER"],
            "password": db_connect_info["DBPASSWORD"],
            "cursorclass": pymysql.cursors.DictCursor
        }

    return db_info
