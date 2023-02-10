from sanic.response import json
import mysql.connector
import jwt
import os

def success_res(data={}):
    data['status'] = "success"
    return json(data)

def error_res(data={}):
    data['status'] = "error"
    return json(data)

def get_dict(data_dict):
    for key, value in data_dict.items():
        if not isinstance(value, (str, int, list, dict)):
            data_dict[key] = str(value)

    return data_dict

def db_connect():

    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )

async def get_one_data(query):
    connection = db_connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    data_dict = cursor.fetchone()
    return get_dict(data_dict)

async def get_all_data(query):
    connection = db_connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    data_list = cursor.fetchall()
    return [ get_dict(row) for row in data_list]

async def paginate(query, count_query, request):
    query_str = query+""
    if request.args.get("order-by") and request.args.get("order-type"):
        query_str = query_str+" ORDER BY {order_by} {order_type}".format(
            order_by=request.args.get("order-by"),
            order_type=request.args.get("order-type")
        )

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))

    offset = (limit*page)-limit

    query_str = query_str+" LIMIT {limit} OFFSET {offset}".format(limit=limit, offset=offset)

    connection = db_connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query_str)
    data_list = cursor.fetchall()

    cursor = connection.cursor()
    cursor.execute(count_query)
    data_count = cursor.fetchone()[0]

    res_data = {
        "count": data_count,
        "list": [ get_dict(row) for row in data_list]
    }
    return res_data

async def insert_data(table_name, data_dict):
    connection = db_connect()
    cursor = connection.cursor()

    query = "INSERT INTO {tablename} ({columns}) VALUES {values};".format(
        tablename=table_name,
        columns=', '.join(data_dict.keys()),
        values=tuple(data_dict.values())
    )
    
    inserted_data = cursor.execute(query)
    connection.commit()
    return inserted_data

async def update_data(table_name, condition_str, data_dict):
    connection = db_connect()
    cursor = connection.cursor()

    data_list = []
    for key, value in data_dict.items():
        data_list.append(key+"='"+value+"'")

    query = "UPDATE {tablename} SET {data_str} WHERE {condition};".format(
        tablename=table_name,
        data_str=", ".join(data_list),
        condition=condition_str
    )
    
    cursor.execute(query)
    return connection.commit()

def jwt_check(jwt_token):
    try:
        return jwt.decode(jwt_token, "synthDeep&*23s2df", algorithms=["HS256"])
    except Exception as e:
        print(e)
        return False

def jwt_user(func):

    def check(self, request, *args, **kwargs):

        try:
            user = jwt_check(request.headers["token"])
            if not user:
                return error_res({"msg": "Invalid token!"})
            elif user['u_user_type'] == "user" or user['u_user_type'] == "client-admin":
                return func(self, request, user, *args, **kwargs)
            else:
                return error_res({"msg": "Invalid token!"})
        except Exception as e:
            print(e)
            return error_res({"msg": "Invalid token!"})

    return check

def jwt_super_admin(func):

    def check(self, request, *args, **kwargs):

        try:
            user = jwt_check(request.headers["token"])
            
            if not user:
                return error_res({"msg": "Invalid token!"})
            elif user['u_user_type'] == "super-admin":
                return func(self, request, user, *args, **kwargs)
            else:
                return error_res({"msg": "Invalid token!"})
        except Exception as e:
            print(e)
            return error_res({"msg": "Invalid token!"})

    return check