from flask import Flask, request, jsonify, Response
from datetime import datetime
import threading
import time
import concurrent.futures  # Import the concurrent.futures module
import os
from dotenv import load_dotenv
import requests
import grpc
import log_pb2
import log_pb2_grpc
import google.protobuf.timestamp_pb2
import psutil
import json
import random
import psycopg2
import logging
from google.protobuf.internal import builder


# from prometheus_client import start_http_server, Counter, Enum, generate_latest, REGISTRY
# from prometheus_client.exposition import make_wsgi_app
# from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, generate_latest, REGISTRY, Gauge
from prometheus_client.exposition import MetricsHandler


app = Flask(__name__)
# metrics = PrometheusMetrics(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variable to track the current master role
current_master_role = 'master'

p = int(os.environ.get("PROMETHEUS_PORT", 4401))
# Define a critical load threshold (e.g., 60 pings per second)
CRITICAL_LOAD_THRESHOLD = 60
pings = 0

user_list = []
service_status = "Healthy"  

# Create Prometheus metrics
counter = Counter(f"chat_gpt_requests_total", f"Requests_{p}")
# requests_counter = Counter(f"chat_gpt_requests_{p}", f"Requests_{p}")
# REGISTRY.register(requests_counter)

# timeouts_counter = Counter('t_an_timeouts_total', 'Timeouts')
# success_counter = Counter('t_an_successful_requests_total', 'Successful Requests')
# error_counter = Counter('t_an_errors_total', 'Errors')
# database_state = Enum('t_an_database_state', 'Database State', states=['connected', 'not connected'])
# register_state = Enum('t_an_register_state', 'Register State', states=['registered', 'not registered'])



# Limit the number of concurrent tasks to 10
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


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
                replica_cursor.execute('SELECT COUNT(*) FROM chat_users')
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

        # Select all data from the chat_users table
        master_cursor.execute('SELECT * FROM chat_users')
        data = master_cursor.fetchall()

        # Close the master connection
        master_conn.close()

        # Connect to each replica and insert data
        for replica_config in db_config['replicas']:
            try:
                replica_conn = psycopg2.connect(**replica_config)
                with replica_conn.cursor() as replica_cursor:
                    replica_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS chat_users (
                            name VARCHAR(255) PRIMARY KEY,
                            name_appearance VARCHAR(255) NOT NULL
                        )
                    ''')
                    # Clear existing data in the replica table
                    replica_cursor.execute('DELETE FROM chat_users')

                    # Insert data into the replica table
                    for row in data:
                        replica_cursor.execute('''
                            INSERT INTO chat_users (name, name_appearance) VALUES (%s, %s)
                            ON CONFLICT (name) DO UPDATE SET name_appearance = EXCLUDED.name_appearance
                        ''', (row[0], row[1]))
                        # replica_cursor.execute('INSERT INTO chat_users (name, name_appearance) VALUES (%s, %s)', (row[0], row[1]))

                # Commit changes outside the cursor context
                replica_conn.commit()
                replica_conn.close()

            except Exception as e:
                logger.error(f"Error connecting to replica or replicating data: {str(e)}")

    except Exception as e:
        raise Exception(f"Error replicating data to replicas: {str(e)}")


def reset_counter():
    while True:
        global pings
        time.sleep(1)
        pings = 0


def check_load():
    global pings
    if pings >= CRITICAL_LOAD_THRESHOLD:
        print("ALERT: Health Monitoring and Alerts")


def run_with_timeout(func, timeout, *args, **kwargs):
    result = None
    exception = None

    def worker():
        nonlocal result, exception
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            exception = e

    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        thread.join()  # Ensure the thread terminates
        raise TimeoutError(f"Request timed out after {timeout} seconds")

    if exception:
        raise exception

    return result

def create_new_obj(new_user_email, current_time):
    return {
        "user_email": new_user_email,
        "when_received": str(current_time)
    }


def send_log_request(serviceName, serviceMessage):
    # Create a gRPC channel to connect to the server
    # channel = grpc.insecure_channel('localhost:5297')  # Replace with the actual server address
    channel = grpc.insecure_channel('notification-server-container:80')  # Replace with the actual server address

    # Create a gRPC stub
    stub = log_pb2_grpc.NotificationStub(channel)

    current_time_seconds = int(time.time())

    # Get the current time in nanoseconds
    current_time_nanoseconds = int(time.time_ns())

    # Create a LogRequest message
    log_request = log_pb2.LogRequest(
        serviceName=serviceName,
        serviceMessage=serviceMessage,
        time= google.protobuf.timestamp_pb2.Timestamp(
            nanos=current_time_nanoseconds % 1_000_000_000,  # Ensure nanoseconds are within the valid range
            seconds=current_time_seconds
        )
    )

    # Send the LogRequest to the server
    response = stub.SaveLogToRabbit(log_request)

    # Handle the response
    if response.isSuccess:
        print("Request was successful on the port 5297.")
    else:
        print("Request failed on the port 5297.")

# @app.route('/metrics')
# def metrics():
#     return generate_latest(REGISTRY)

@app.route('/chat', methods=['POST'])
def chat():
    
    if request.method == 'POST':
        global pings
        pings += 1
        check_load()
        timeout_seconds = 5
        timeout_event = threading.Event()

        def timeout_handler():
            timeout_event.set()

        timer_thread = threading.Timer(timeout_seconds, timeout_handler)
        timer_thread.start()
        if timeout_event.is_set():
            print("Request timed out.")

        new_user_email = request.json.get('user_email')  
        new_question_command = request.json.get('question')  
        new_question_prompt = ""

        try:
            connection = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="chat-gpt-database",
                # host="192.168.2.150",
                # port="5433",
                database="chat-gpt-db"
            )

            cursor = connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS question_command_table (
                id serial PRIMARY KEY,
                new_question_command VARCHAR(255) UNIQUE,
                new_question_prompt VARCHAR(255)
            );
            """

            cursor.execute(create_table_query)
            connection.commit()
            # cursor.execute("TRUNCATE question_command_table;")
            # connection.commit()
            # print("Table 'question_command_table' has been cleared.")

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", ('question_command_table',))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("Table 'question_command_table' exists.")
            else:
                print("Table 'question_command_table' does not exist. You may need to create it.")

            # Check if 'new_question' exists in the table
            cursor.execute("SELECT new_question_prompt FROM question_command_table WHERE new_question_command = %s", (new_question_command,))
            existing_description = cursor.fetchone()
            if existing_description is not None:
                print("It EXISTS")
                new_question_prompt = existing_description[0]
            else:
                print("It DOES NOT EXIST")
                new_question_prompt = new_question_command


        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        

        current_time = datetime.now()
        
        # print(new_question)
        
        
        # Set your OpenAI API key
        # api_key = "a"


        load_dotenv()
        api_key = os.environ.get('YOUR_API_KEY')

         # Retrieve the API key from the database
        # api_key = get_api_key()


        # print(api_key)
        # print(type(api_key))
        # api_key = str(api_key)

        # Define the API endpoint
        api_endpoint = "https://api.openai.com/v1/chat/completions"

        # Define the prompt you want to send to the model
        prompt = new_question_prompt

        # Send a POST request to the API
        response = requests.post(
            api_endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        if timeout_event.is_set():
            print("Request timed out.")

        # Parse and print the response
        if response.status_code == 200:
            print("Successful request to Chat GPT")
            data = response.json()
            if "choices" in data and data["choices"]:
                completions = data["choices"][0]["message"]["content"]
            else:
                completions = "No completions available"
        else:
            completions = "Request failed with status code: " + str(response.status_code)
        # completions = "ChatGPT is here to answer!"
        try:
            new_obj = run_with_timeout(
                create_new_obj,
                timeout=10,  # Set a timeout of 10 seconds
                new_user_email=new_user_email,
                current_time=current_time
            )
            if timeout_event.is_set():
                print("Request timed out.")

            user_list.append(new_obj)
            # Call the gRPC function to send log request
            current_endpoint = request.endpoint
            send_log_request("Chat GPT Service", f"{current_endpoint} - Endpoint from Chat GPT Service was successful")
            # completions = new_question_prompt
            return jsonify({"response": completions}), 200
            # return jsonify(user_list), 201
        except TimeoutError:
            return jsonify({"error": "Request timed out"}), 500
        
        return jsonify({}), 200


@app.route('/addcommand', methods=['POST'])
def command():
    if request.method == 'POST':
        global pings
        pings += 1
        # print("Request received")
        # print(pings)
        check_load()
        timeout_seconds = 5
        timeout_event = threading.Event()

        def timeout_handler():
            timeout_event.set()
            # print("Timer is set.")

        timer_thread = threading.Timer(timeout_seconds, timeout_handler)
        timer_thread.start()
        # time.sleep(3)
        if timeout_event.is_set():
            print("Request timed out.")
        # new_user_email = request.form['user_email']
        # new_question = request.form['question']

        new_question_command = request.json.get('command')  # Access data as JSON
        new_question_prompt = request.json.get('question')
        # new_question_description = "new_question_description_1"

        try:
            connection = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="chat-gpt-database",
                # host="192.168.2.150",
                # port="5433",
                database="chat-gpt-db"
            )

            cursor = connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS question_command_table (
                id serial PRIMARY KEY,
                new_question_command VARCHAR(255) UNIQUE,
                new_question_prompt VARCHAR(255)
            );
            """

            cursor.execute(create_table_query)
            connection.commit()

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", ('question_command_table',))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("Table 'question_command_table' exists.")
            else:
                print("Table 'question_command_table' does not exist. You may need to create it.")

            
            # Check if 'new_question_command' exists in the table
            cursor.execute("SELECT new_question_prompt FROM question_command_table WHERE new_question_command = %s", (new_question_command,))
            existing_description = cursor.fetchone()
            if existing_description is not None:
                print("It EXISTS")
                new_question_prompt = existing_description[0]
                print(f"Exists {new_question_command} command for Question prompt: {new_question_prompt}")
            else:
                print("It DOES NOT EXIST")
                insert_data_query = "INSERT INTO question_command_table (new_question_command, new_question_prompt) VALUES (%s, %s) RETURNING new_question_prompt;"
                data_to_insert = (new_question_command, new_question_prompt)
                cursor.execute(insert_data_query, data_to_insert)
                connection.commit()
                print(f"Was created {new_question_command} command for Question prompt: {new_question_prompt}")


        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

        return jsonify({"response": f"Was created {new_question_command} command for Question prompt: {new_question_prompt}"}), 200
        
        return jsonify({}), 200


    

@app.route('/status', methods=['GET'])
def get_status():
    timeout_seconds = 2
    timeout_event = threading.Event()
    counter.inc()
    # requests_counter.inc()

    def timeout_handler():
        timeout_event.set()

    timer_thread = threading.Timer(timeout_seconds, timeout_handler)
    timer_thread.start()
    if timeout_event.is_set():
        print("Request timed out.")
    global service_status
    return jsonify({"status": service_status})

def is_service_healthy():
    # Check system resource usage
    try:
        # Check CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)  # Monitor CPU usage for 1 second
        if cpu_usage < 80:
            # CPU usage is within acceptable limits
            pass
        else:
            # CPU usage is high, consider service as unhealthy
            return False

        # Check memory usage
        memory_usage = psutil.virtual_memory().percent
        if memory_usage < 90:
            # Memory usage is within acceptable limits
            pass
        else:
            # Memory usage is high, consider service as unhealthy
            return False

        # If all checks pass, consider the service as healthy
        return True
    except Exception as e:
        # Handle exceptions and consider the service as unhealthy
        return False

# In the check_health function, set service_status based on health checks
def check_health():
    global service_status
    while True:
        if is_service_healthy():
            service_status = "Healthy"
        else:
            service_status = "Unhealthy"
        time.sleep(10)  # Check health every 10 seconds


# # Endpoint for Prometheus to scrape metrics
# app.route('/metrics')(MetricsHandler.factory(REGISTRY))

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), content_type='text/plain')


# @app.route('/get_connection', methods=['GET'])
# def get_connection():
#     try:
#         # Attempt to connect to the PostgreSQL database
#         conn = psycopg2.connect(
#                 user="postgres",
#                 password="password",
#                 # host="localhost",
#                 host="chat-gpt-database",
#                 # host="192.168.2.150",
#                 # port="5433",
#                 database="chat-gpt-db"
#             )
#         conn.close()
#         return jsonify({"status": "ok"})
#     except Exception as e:
#         return jsonify({"status": "not ok", "error": str(e)}), 500


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
            CREATE TABLE IF NOT EXISTS chat_users (
                name VARCHAR(255) PRIMARY KEY,
                name_appearance VARCHAR(255) NOT NULL
            )
        ''')

        # Insert user data into the table
        cursor.execute('''
            INSERT INTO chat_users (name, name_appearance) VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET name_appearance = EXCLUDED.name_appearance
        ''', (data['name'], data['name_appearance']))
        
        # cursor.execute('INSERT INTO chat_users (name, name_appearance) VALUES (%s, %s)', (data['name'], data['name_appearance']))

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

    

# # Endpoint for creating a user in chat_gpt_service
# @app.route('/create', methods=['POST'])
# def create_user():
#     data = request.get_json()

#     try:
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(
#                 user="postgres",
#                 password="password",
#                 # host="localhost",
#                 host="chat-gpt-database",
#                 # host="192.168.2.150",
#                 # port="5433",
#                 database="chat-gpt-db"
#             )
#         cursor = conn.cursor()

#         # Create the user table if it doesn't exist
#         cursor.execute('''
#             CREATE TABLE IF NOT EXISTS chat_users (
#                 name VARCHAR(255) PRIMARY KEY,
#                 name_appearance VARCHAR(255) NOT NULL
#             )
#         ''')

#         # Insert user data into the table
#         cursor.execute('INSERT INTO chat_users (name, name_appearance) VALUES (%s, %s)', (data['name'], data['name_appearance']))

#         # Commit the changes and close the connection
#         conn.commit()
#         conn.close()

#         return jsonify({"status": "success", "message": "User created successfully in chat_gpt_service."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

# @app.route('/undo', methods=['DELETE'])
# def undo_change():
#     data = request.get_json()

#     try:
#         # Connect to the PostgreSQL database
#         conn = psycopg2.connect(
#                 user="postgres",
#                 password="password",
#                 # host="localhost",
#                 host="chat-gpt-database",
#                 # host="192.168.2.150",
#                 # port="5433",
#                 database="chat-gpt-db"
#             )
#         cursor = conn.cursor()

#         # Delete the user with the given name and name_appearance from the table
#         cursor.execute('DELETE FROM chat_users WHERE name = %s AND name_appearance = %s', (data['name'], data['name_appearance']))

#         # Commit the changes and close the connection
#         conn.commit()
#         conn.close()

#         return jsonify({"status": "success", "message": "Change undone in chat_gpt_service."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500


# Endpoint for undoing the recent change
@app.route('/undo', methods=['DELETE'])
def undo_change():
    data = request.get_json()

    try:
        # Connect to the master PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete the user with the given name and name from the table
        cursor.execute('DELETE FROM chat_users WHERE name = %s AND name_appearance = %s', (data['name'], data['name_appearance']))

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
        master_cursor.execute('SELECT * FROM chat_users')
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
                replica_cursor.execute('SELECT * FROM chat_users')
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
    health_check_thread = threading.Thread(target=check_health)
    health_check_thread.daemon = True
    health_check_thread.start()

    reset_thread = threading.Thread(target=reset_counter, daemon=True)

    reset_thread.start()

    
    app.run(host="0.0.0.0", port=5000, debug=True)


# py chat_gpt_service\chat_gpt_service.py