# # # # from flask import Flask, request, jsonify
# # # # import psycopg2

# # # # app = Flask(__name__)

# # # # # Endpoint for checking connection health
# # # # @app.route('/get_connection', methods=['GET'])
# # # # def get_connection():
# # # #     try:
# # # #         # Attempt to connect to the PostgreSQL database
# # # #         conn = psycopg2.connect(
# # # #                 user="postgres",
# # # #                 password="password",
# # # #                 # host="localhost",
# # # #                 host="user-database",
# # # #                 # host="192.168.2.150",
# # # #                 # port="5433",
# # # #                 database="user-db"
# # # #                 # 'dbname': 'your_database_name',
# # # #                 # 'user': 'your_username',
# # # #                 # 'password': 'your_password',
# # # #                 # 'host': 'your_host',
# # # #                 # 'port': 'your_port'
# # # #             )
# # # #         conn.close()
# # # #         return jsonify({"status": "ok"})
# # # #     except Exception as e:
# # # #         return jsonify({"status": "not ok", "error": str(e)}), 500

# # # # # Endpoint for creating a user
# # # # @app.route('/create', methods=['POST'])
# # # # def create_user():
# # # #     data = request.get_json()

# # # #     try:
# # # #         # Connect to the PostgreSQL database
# # # #         conn = psycopg2.connect(
# # # #                 user="postgres",
# # # #                 password="password",
# # # #                 # host="localhost",
# # # #                 host="user-database",
# # # #                 # host="192.168.2.150",
# # # #                 # port="5433",
# # # #                 database="user-db"
# # # #                 # 'dbname': 'your_database_name',
# # # #                 # 'user': 'your_username',
# # # #                 # 'password': 'your_password',
# # # #                 # 'host': 'your_host',
# # # #                 # 'port': 'your_port'
# # # #             )
# # # #         cursor = conn.cursor()

# # # #         # Create the user table if it doesn't exist
# # # #         cursor.execute('''
# # # #             CREATE TABLE IF NOT EXISTS users (
# # # #                 email VARCHAR(255) PRIMARY KEY,
# # # #                 name VARCHAR(255) NOT NULL
# # # #             )
# # # #         ''')

# # # #         # Insert user data into the table
# # # #         cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (data['email'], data['name']))

# # # #         # Commit the changes and close the connection
# # # #         conn.commit()
# # # #         conn.close()

# # # #         return jsonify({"status": "success", "message": "User created successfully."})
# # # #     except Exception as e:
# # # #         return jsonify({"status": "error", "message": str(e)}), 500

# # # # # Endpoint for undoing the recent change
# # # # @app.route('/undo', methods=['DELETE'])
# # # # def undo_change():
# # # #     data = request.get_json()

# # # #     try:
# # # #         # Connect to the PostgreSQL database
# # # #         conn = psycopg2.connect(
# # # #                 user="postgres",
# # # #                 password="password",
# # # #                 # host="localhost",
# # # #                 host="user-database",
# # # #                 # host="192.168.2.150",
# # # #                 # port="5433",
# # # #                 database="user-db"
# # # #                 # 'dbname': 'your_database_name',
# # # #                 # 'user': 'your_username',
# # # #                 # 'password': 'your_password',
# # # #                 # 'host': 'your_host',
# # # #                 # 'port': 'your_port'
# # # #             )
# # # #         cursor = conn.cursor()

# # # #         # Delete the user with the given email and name from the table
# # # #         cursor.execute('DELETE FROM users WHERE email = %s AND name = %s', (data['email'], data['name']))

# # # #         # Commit the changes and close the connection
# # # #         conn.commit()
# # # #         conn.close()

# # # #         return jsonify({"status": "success", "message": "Change undone."})
# # # #     except Exception as e:
# # # #         return jsonify({"status": "error", "message": str(e)}), 500

# # # # if __name__ == '__main__':
# # # #     app.run(host="0.0.0.0", port=6000, debug=True)


# from flask import Flask, request, jsonify
# import psycopg2
# from psycopg2 import sql
# import logging


# app = Flask(__name__)

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Database connection configuration
# db_config = {
#     'master': {
#         'user': 'postgres',
#         'password': 'password',
#         'host': 'user-database',
#         'database': 'user-db',
#     },
#     'replicas': [
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database1', 'database': 'user-db1'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database2', 'database': 'user-db2'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database3', 'database': 'user-db3'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database4', 'database': 'user-db4'},
#     ],
# }


# # Function to get a connection based on the specified role (master or replicas)
# def get_db_connection(role='master'):
#     config = db_config.get(role)
#     if config:
#         try:
#             if role == 'master':
#                 return psycopg2.connect(**config)
#             else:
#                 # Return the first replica connection from the list
#                 return psycopg2.connect(**config[0])
#         except Exception as e:
#             raise Exception(f"Error connecting to {role} database: {str(e)}")
#     else:
#         raise Exception(f"Invalid database role: {role}")


# # Function to replicate data from master to replicas
# def replicate_data():
#     try:
#         # Connect to the master PostgreSQL database
#         master_conn = get_db_connection(role='master')
#         master_cursor = master_conn.cursor()

#         # Select all data from the users table
#         master_cursor.execute('SELECT * FROM users')
#         data = master_cursor.fetchall()

#         # Close the master connection
#         master_conn.close()

#         # Connect to each replica and insert data
#         for replica_config in db_config['replicas']:
#             try:
#                 replica_conn = psycopg2.connect(**replica_config)
#                 with replica_conn.cursor() as replica_cursor:
#                     replica_cursor.execute('''
#                         CREATE TABLE IF NOT EXISTS users (
#                             email VARCHAR(255) PRIMARY KEY,
#                             name VARCHAR(255) NOT NULL
#                         )
#                     ''')
#                     # Clear existing data in the replica table
#                     replica_cursor.execute('DELETE FROM users')

#                     # Insert data into the replica table
#                     for row in data:
#                         replica_cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (row[0], row[1]))

#                 # Commit changes outside the cursor context
#                 replica_conn.commit()
#                 replica_conn.close()

#             except Exception as e:
#                 logger.error(f"Error connecting to replica or replicating data: {str(e)}")

#     except Exception as e:
#         raise Exception(f"Error replicating data to replicas: {str(e)}")


# # Endpoint for checking connection health
# @app.route('/get_connection', methods=['GET'])
# def get_connection():
#     try:
#         # Attempt to connect to the master PostgreSQL database
#         conn = get_db_connection()
#         conn.close()
#         return jsonify({"status": "ok"})
#     except Exception as e:
#         # Log the error using the logger
#         logger.error(f"Error in health check: {str(e)}")
#         return jsonify({"status": "not ok", "error": str(e)}), 500


# # Endpoint for creating a user
# @app.route('/create', methods=['POST'])
# def create_user():
#     data = request.get_json()

#     try:
#         # Attempt to connect to the master PostgreSQL database for health check
#         conn_health_check = get_db_connection()
#         conn_health_check.close()
#         logger.info("Health check successful.")

#         # Connect to the master PostgreSQL database
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Create the user table if it doesn't exist
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS users (
#                 email VARCHAR(255) PRIMARY KEY,
#                 name VARCHAR(255) NOT NULL
#             )
#         ''')

#         # Insert user data into the table
#         cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (data['email'], data['name']))

#         # Commit the changes and close the connection
#         conn.commit()
#         conn.close()

#         # Replicate data to replicas
#         replicate_data()

#         return jsonify({"status": "success", "message": "User created successfully."})
#     except Exception as e:
#         # Log the error and health check status
#         logger.error(f"Error in user creation: {str(e)}")
#         return jsonify({"status": "error", "message": str(e)}), 500


# # Endpoint for undoing the recent change
# @app.route('/undo', methods=['DELETE'])
# def undo_change():
#     data = request.get_json()

#     try:
#         # Connect to the master PostgreSQL database
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # Delete the user with the given email and name from the table
#         cursor.execute('DELETE FROM users WHERE email = %s AND name = %s', (data['email'], data['name']))

#         # Commit the changes and close the connection
#         conn.commit()
#         conn.close()

#         # Replicate data to replicas
#         replicate_data()

#         return jsonify({"status": "success", "message": "Change undone."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# # Endpoint for getting stored data
# @app.route('/get_data', methods=['GET'])
# def get_data():
#     try:
#         # Connect to the master PostgreSQL database
#         master_conn = get_db_connection()
#         master_cursor = master_conn.cursor()

#         # Select data from the users table in the master database
#         master_cursor.execute('SELECT * FROM users')
#         master_data = master_cursor.fetchall()

#         # Close the master connection
#         master_conn.close()

#         # Connect to each replica and fetch data
#         replica_data = {}
#         for i, replica_config in enumerate(db_config['replicas'], 1):
#             try:
#                 replica_conn = get_db_connection(role='replicas')
#                 replica_cursor = replica_conn.cursor()

#                 # Select data from the users table in the replica
#                 replica_cursor.execute('SELECT * FROM users')
#                 data = replica_cursor.fetchall()

#                 # Close the replica connection
#                 replica_conn.close()

#                 # Store replica data in the response dictionary
#                 replica_data[f"replica_{i}"] = {"data": data}

#             except Exception as e:
#                 logger.error(f"Error connecting to replica or fetching data: {str(e)}")

#         # Combine data from master and replicas into a single response
#         response_data = {
#             "master": {"data": master_data},
#             "replicas": replica_data,
#             "status": "success"
#         }

#         return jsonify(response_data)

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500



# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=6000, debug=True)



from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import sql
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variable to track the current master role
current_master_role = 'master'

# # Database connection configuration
# db_config = {
#     'master': {
#         'user': 'postgres',
#         'password': 'password',
#         'host': 'user-database',
#         'database': 'user-db',
#     },
#     'replicas': [
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database1', 'database': 'user-db1'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database2', 'database': 'user-db2'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database3', 'database': 'user-db3'},
#         {'user': 'postgres', 'password': 'password', 'host': 'user-database4', 'database': 'user-db4'},
#     ],
# }

def get_db_config(role='master'):
    return {
        'user': os.getenv(f'DB_USER_{role.upper()}'),
        'password': os.getenv(f'DB_PASSWORD_{role.upper()}'),
        'host': os.getenv(f'DB_HOST_{role.upper()}'),
        'database': os.getenv(f'DB_NAME_{role.upper()}'),
    }

# Database connection configuration
db_config = {
    'master': get_db_config(role='master'),
    'replicas': [get_db_config(role=f'replica_{i+1}') for i in range(4)],
}

# Function to check if the master is available
def is_master_available():
    try:
        conn = get_db_connection(role='master')
        conn.close()
        return True
    except:
        return False

def perform_failover():
    global current_master_role

    # Check if the master is available
    if not is_master_available():
        logger.warning("Master database not available. Performing failover.")

        # Calculate the data sizes for each replica
        replica_data_sizes = {}
        for i, replica_config in enumerate(db_config['replicas'], 1):
            try:
                replica_conn = psycopg2.connect(**replica_config)
                replica_cursor = replica_conn.cursor()

                # Select data from the users table in the replica
                replica_cursor.execute('SELECT COUNT(*) FROM users')
                data_size = replica_cursor.fetchone()[0]

                # Close the replica connection
                replica_conn.close()

                # Store replica data size in the dictionary
                replica_data_sizes[f"replica_{i}"] = data_size

            except Exception as e:
                logger.error(f"Error connecting to replica or fetching data size: {str(e)}")

        # Choose the replica with the most significant amount of data as the new master
        new_master_index = max(replica_data_sizes, key=replica_data_sizes.get)
        new_master_config = db_config['replicas'][int(new_master_index.split('_')[1]) - 1]

        # Update the application configuration to use the new master
        db_config['master'] = new_master_config
        current_master_role = new_master_index

        logger.info(f"Failover complete. New master: {new_master_config}")

        # Attempt to connect to the new master for a health check
        if not is_master_available():
            # Log the error using the logger
            logger.error("Failover health check failed.")
            # Return a failover response
            return None

    return new_master_config  # Return the new master configuration



# Function to get a connection based on the specified role (master or replicas)
def get_db_connection(role='master'):
    global current_master_role

    config = db_config.get(role)
    if config:
        try:
            if role == 'master':
                # Attempt to connect to the master PostgreSQL database
                return psycopg2.connect(**config)
            else:
                # If the master is not available, perform failover
                if not is_master_available():
                    new_master_config = perform_failover()
                    if new_master_config:
                        # Update the current master role and configuration
                        current_master_role = 'replica_1'
                        return psycopg2.connect(**new_master_config)
                    else:
                        raise Exception("Failover failed. No new master configuration.")
                else:
                    # Return the first replica connection from the list
                    return psycopg2.connect(**config[0])
        except Exception as e:
            raise Exception(f"Error connecting to {role} database: {str(e)}")
    else:
        raise Exception(f"Invalid database role: {role}")


# Function to replicate data from master to replicas
def replicate_data():
    try:
        # Connect to the master PostgreSQL database
        master_conn = get_db_connection(role='master')
        master_cursor = master_conn.cursor()

        # Select all data from the users table
        master_cursor.execute('SELECT * FROM users')
        data = master_cursor.fetchall()

        # Close the master connection
        master_conn.close()

        # Connect to each replica and insert data
        for replica_config in db_config['replicas']:
            try:
                replica_conn = psycopg2.connect(**replica_config)
                with replica_conn.cursor() as replica_cursor:
                    replica_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            email VARCHAR(255) PRIMARY KEY,
                            name VARCHAR(255) NOT NULL
                        )
                    ''')
                    # Clear existing data in the replica table
                    replica_cursor.execute('DELETE FROM users')

                    # Insert data into the replica table
                    for row in data:
                        replica_cursor.execute('''
                            INSERT INTO users (email, name) VALUES (%s, %s)
                            ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
                        ''', (row[0], row[1]))
                        # replica_cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (row[0], row[1]))

                # Commit changes outside the cursor context
                replica_conn.commit()
                replica_conn.close()

            except Exception as e:
                logger.error(f"Error connecting to replica or replicating data: {str(e)}")

    except Exception as e:
        raise Exception(f"Error replicating data to replicas: {str(e)}")

# Endpoint for checking connection health
@app.route('/get_connection', methods=['GET'])
def get_connection():
    try:
        # Attempt to connect to the master PostgreSQL database
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        # Log the error using the logger
        logger.error(f"Error in health check: {str(e)}")

        # Perform failover if the master is unavailable
        failover_response = perform_failover()
        if failover_response:
            return failover_response

        return jsonify({"status": "not ok", "error": str(e)}), 500
    
# Endpoint for creating a user
@app.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()

    try:
        # Attempt to connect to the master PostgreSQL database for health check
        conn_health_check = get_db_connection()
        conn_health_check.close()
        logger.info("Health check successful.")

        # Connect to the master PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the user table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        ''')

        # Insert user data into the table
        cursor.execute('''
            INSERT INTO users (email, name) VALUES (%s, %s)
            ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name
        ''', (data['email'], data['name']))
        # cursor.execute('INSERT INTO users (email, name) VALUES (%s, %s)', (data['email'], data['name']))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Replicate data to replicas
        replicate_data()

        return jsonify({"status": "success", "message": "User created successfully."})
    except Exception as e:
        # Log the error and health check status
        logger.error(f"Error in user creation: {str(e)}")

        # Perform failover if the master is unavailable
        failover_response = perform_failover()
        if failover_response:
            logger.info("Retrying user creation after failover.")
            return create_user()  # Retry the user creation process with the new master configuration

        return jsonify({"status": "error", "message": str(e)}), 500

    
# Endpoint for undoing the recent change
@app.route('/undo', methods=['DELETE'])
def undo_change():
    data = request.get_json()

    try:
        # Connect to the master PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete the user with the given email and name from the table
        cursor.execute('DELETE FROM users WHERE email = %s AND name = %s', (data['email'], data['name']))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Replicate data to replicas
        replicate_data()

        return jsonify({"status": "success", "message": "Change undone."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Endpoint for getting stored data
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Connect to the master PostgreSQL database
        master_conn = get_db_connection()
        master_cursor = master_conn.cursor()

        # Select data from the users table in the master database
        master_cursor.execute('SELECT * FROM users')
        master_data = master_cursor.fetchall()

        # Close the master connection
        master_conn.close()

        # Connect to each replica and fetch data
        replica_data = {}
        for i, replica_config in enumerate(db_config['replicas'], 1):
            try:
                replica_conn = get_db_connection(role='replicas')
                replica_cursor = replica_conn.cursor()

                # Select data from the users table in the replica
                replica_cursor.execute('SELECT * FROM users')
                data = replica_cursor.fetchall()

                # Close the replica connection
                replica_conn.close()

                # Store replica data in the response dictionary
                replica_data[f"replica_{i}"] = {"data": data}

            except Exception as e:
                logger.error(f"Error connecting to replica or fetching data: {str(e)}")

        # Determine the master role after failover
        master_role = 'master' if current_master_role == 'master' else f"master-{current_master_role}"

        # Combine data from master and replicas into a single response
        response_data = {
            master_role: {"data": master_data},
            **replica_data,
            "status": "success"
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000, debug=True)
