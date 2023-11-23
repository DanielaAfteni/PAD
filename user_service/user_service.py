from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# Endpoint for checking connection health
@app.route('/get_connection', methods=['GET'])
def get_connection():
    try:
        # Attempt to connect to the PostgreSQL database
        conn = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="user-database",
                # host="192.168.2.150",
                # port="5433",
                database="user-db"
                # 'dbname': 'your_database_name',
                # 'user': 'your_username',
                # 'password': 'your_password',
                # 'host': 'your_host',
                # 'port': 'your_port'
            )
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "not ok", "error": str(e)}), 500

# Endpoint for creating a user
@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="user-database",
                # host="192.168.2.150",
                # port="5433",
                database="user-db"
                # 'dbname': 'your_database_name',
                # 'user': 'your_username',
                # 'password': 'your_password',
                # 'host': 'your_host',
                # 'port': 'your_port'
            )
        cursor = conn.cursor()

        # Create the user table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        # Insert user data into the table
        cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (data['email'], data['name']))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "User created successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint for undoing the recent change
@app.route('/undo', methods=['DELETE'])
def undo_change():
    data = request.get_json()

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="user-database",
                # host="192.168.2.150",
                # port="5433",
                database="user-db"
                # 'dbname': 'your_database_name',
                # 'user': 'your_username',
                # 'password': 'your_password',
                # 'host': 'your_host',
                # 'port': 'your_port'
            )
        cursor = conn.cursor()

        # Delete the user with the given email and name from the table
        cursor.execute('DELETE FROM users WHERE email = %s AND name = %s', (data['email'], data['name']))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "Change undone."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)





# from flask import Flask, request, jsonify
# import psycopg2
# from psycopg2 import extras
# import random
# import time

# app = Flask(__name__)

# # Database configuration for master
# MASTER_DB_CONFIG = {
#     "user": "postgres",
#     "password": "password",
#     "host": "postgres-database1",
#     "database": "postgres-db1"
# }

# # Database configurations for 4 slave databases
# SLAVE_DB_CONFIGS = [
#     {
#         "user": "postgres",
#         "password": "password",
#         "host": "postgres-slave1",
#         "database": "postgres-db2"
#     },
#     {
#         "user": "postgres",
#         "password": "password",
#         "host": "postgres-slave2",
#         "database": "postgres-db3"
#     },
#     {
#         "user": "postgres",
#         "password": "password",
#         "host": "postgres-slave3",
#         "database": "postgres-db4"
#     },
#     {
#         "user": "postgres",
#         "password": "password",
#         "host": "postgres-slave4",
#         "database": "postgres-db5"
#     }
# ]

# def get_master_connection():
#     return psycopg2.connect(**MASTER_DB_CONFIG)

# def get_slave_connections():
#     return [psycopg2.connect(**config) for config in SLAVE_DB_CONFIGS]

# def synchronize_data():
#     try:
#         # Connect to the master database
#         with get_master_connection() as master_conn:
#             with master_conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
#                 # Example: Select all users from the table on the master
#                 cursor.execute('SELECT * FROM users')
#                 master_result = cursor.fetchall()

#         # Connect to all 4 slave databases
#         slave_connections = get_slave_connections()

#         for slave_conn in slave_connections:
#             with slave_conn.cursor() as cursor:
#                 # Example: Delete all existing data in the slave user table
#                 cursor.execute('DELETE FROM users')

#                 # Example: Insert the master data into the slave user table
#                 for row in master_result:
#                     cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (row['email'], row['name']))

#             # Commit the changes to the slave database
#             slave_conn.commit()

#     finally:
#         # Close all slave connections
#         for slave_conn in slave_connections:
#             slave_conn.close()

# # Endpoint for checking connection health
# @app.route('/get_connection', methods=['GET'])
# def get_connection():
#     try:
#         # Attempt to connect to the master database
#         with get_master_connection() as conn:
#             conn.close()
#         return jsonify({"status": "ok"})
#     except Exception as e:
#         return jsonify({"status": "not ok", "error": str(e)}), 500

# # Endpoint for creating a user
# @app.route('/create', methods=['POST'])
# def create_user():
#     data = request.get_json()

#     try:
#         # Connect to the master database
#         with get_master_connection() as conn:
#             with conn.cursor() as cursor:
#                 # Create the user table if it doesn't exist
#                 cursor.execute('''
#                     CREATE TABLE IF NOT EXISTS users (
#                         email VARCHAR(255) PRIMARY KEY,
#                         name VARCHAR(255) NOT NULL
#                     )
#                 ''')

#                 # Insert user data into the table
#                 cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (data['email'], data['name']))

#         # Synchronize data after creating a user
#         synchronize_data()

#         return jsonify({"status": "success", "message": "User created successfully."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# # Endpoint for undoing the recent change
# @app.route('/undo', methods=['DELETE'])
# def undo_change():
#     data = request.get_json()

#     try:
#         # Connect to the master database
#         with get_master_connection() as conn:
#             with conn.cursor() as cursor:
#                 # Delete the user with the given email and name from the table
#                 cursor.execute('DELETE FROM users WHERE email = %s AND name = %s', (data['email'], data['name']))

#         # Synchronize data after undoing the change
#         synchronize_data()

#         return jsonify({"status": "success", "message": "Change undone."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# # Endpoint for reading data (master and all 4 slaves)
# @app.route('/read', methods=['GET'])
# def read_data():
#     try:
#         # Synchronize data before reading
#         synchronize_data()

#         # Connect to the master database
#         with get_master_connection() as master_conn:
#             with master_conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
#                 # Example: Select all users from the table on the master
#                 cursor.execute('SELECT * FROM users')
#                 master_result = cursor.fetchall()

#         # Connect to all 4 slave databases
#         slave_connections = get_slave_connections()
#         slave_results = []

#         for slave_conn in slave_connections:
#             with slave_conn.cursor(cursor_factory=extras.RealDictCursor) as cursor:
#                 # Example: Select all users from the table on each slave
#                 cursor.execute('SELECT * FROM users')
#                 slave_results.extend(cursor.fetchall())

#         return jsonify({
#             "status": "success",
#             "data": {
#                 "master": master_result,
#                 "slaves": slave_results
#             }
#         })
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500
#     finally:
#         # Close all slave connections
#         for slave_conn in slave_connections:
#             slave_conn.close()

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=6000, debug=True)
