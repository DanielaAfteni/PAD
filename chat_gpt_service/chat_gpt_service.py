from flask import Flask, request, jsonify
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


# connection = sqlite3.connect("config.db")
# cursor = connection.cursor()

# cursor.execute('''CREATE TABLE IF NOT EXISTS api_config (
#                     id INTEGER PRIMARY KEY,
#                     api_key TEXT
#                  )''')

# # Commit the changes and close the connection
# connection.commit()
# connection.close()

app = Flask(__name__)


# Define a critical load threshold (e.g., 60 pings per second)
CRITICAL_LOAD_THRESHOLD = 60
pings = 0

user_list = []
service_status = "Healthy"  # Initial status


# create_table_query = """
# CREATE TABLE IF NOT EXISTS my_table (
#     id serial PRIMARY KEY,
#     new_question VARCHAR(255) UNIQUE,
#     new_question_description VARCHAR(255)
# );
# """


# Limit the number of concurrent tasks to 10
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

def reset_counter():
    while True:
        global pings
        time.sleep(1)
        pings = 0
        # print("Resetting counter")
        # print(pings)


def check_load():
    global pings
    if pings >= CRITICAL_LOAD_THRESHOLD:
        print("ALERT: Health Monitoring and Alerts")


def send_alert(alert_message):
    # Implement the logic to send an alert, for example, send an email or push notification
    # You can use third-party libraries for sending alerts

    print("ALERT:", alert_message)


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



@app.route('/chat', methods=['POST'])
def chat():
    
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

        new_user_email = request.json.get('user_email')  # Access data as JSON
        new_question_command = request.json.get('question')  # Access data as JSON
        new_question_prompt = ""

        try:
            connection = psycopg2.connect(
                user="postgres",
                password="password",
                # host="localhost",
                host="postgres-database",
                # host="192.168.2.150",
                # port="5433",
                database="postgres-db"
            )

            cursor = connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS my_table (
                id serial PRIMARY KEY,
                new_question_command VARCHAR(255) UNIQUE,
                new_question_prompt VARCHAR(255)
            );
            """

            cursor.execute(create_table_query)
            connection.commit()
            # cursor.execute("TRUNCATE my_table;")
            # connection.commit()
            # print("Table 'my_table' has been cleared.")

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", ('my_table',))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("Table 'my_table' exists.")
            else:
                print("Table 'my_table' does not exist. You may need to create it.")

            

            # Check if 'new_question' exists in the table
            cursor.execute("SELECT new_question_prompt FROM my_table WHERE new_question_command = %s", (new_question_command,))
            existing_description = cursor.fetchone()
            if existing_description is not None:
                print("It EXISTS")
                new_question_prompt = existing_description[0]
            else:
                print("It DOES NOT EXIST")
                new_question_prompt = new_question_command
                # # If 'new_question' doesn't exist, insert it and its description
                # insert_data_query = "INSERT INTO my_table (new_question, new_question_prompt) VALUES (%s, %s) RETURNING new_question_prompt;"
                # data_to_insert = (new_question, "Default Description")  # You can set your own default description
                # cursor.execute(insert_data_query, data_to_insert)
                # connection.commit()
                # new_question_prompt = "Default Description"  # Use the default description
                # If 'new_question' doesn't exist, insert it and its description
                # insert_data_query = "INSERT INTO my_table (new_question_command, new_question_prompt) VALUES (%s, %s) RETURNING new_question_prompt;"
                # data_to_insert = (new_question_command, new_question_prompt)  # You can set your own default description
                # cursor.execute(insert_data_query, data_to_insert)
                # connection.commit()
                # new_question_prompt = "Default Description"  # Use the default description
                




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
            data = response.json()
            if "choices" in data and data["choices"]:
                completions = data["choices"][0]["message"]["content"]
            else:
                completions = "No completions available"
        else:
            completions = "Request failed with status code: " + str(response.status_code)
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
                host="postgres-database",
                # host="192.168.2.150",
                # port="5433",
                database="postgres-db"
            )

            cursor = connection.cursor()
            #         # SQL command to delete the table
            # delete_table_query = f'DROP TABLE IF EXISTS my_table;'

            # # Execute the SQL command to delete the table
            # cursor.execute(delete_table_query)
            # connection.commit()
            # print("the table was deleted")

            create_table_query = """
            CREATE TABLE IF NOT EXISTS my_table (
                id serial PRIMARY KEY,
                new_question_command VARCHAR(255) UNIQUE,
                new_question_prompt VARCHAR(255)
            );
            """

            cursor.execute(create_table_query)
            connection.commit()
            # cursor.execute("TRUNCATE my_table;")
            # connection.commit()
            # print("Table 'my_table' has been cleared.")

            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", ('my_table',))
            table_exists = cursor.fetchone()[0]

            if table_exists:
                print("Table 'my_table' exists.")
            else:
                print("Table 'my_table' does not exist. You may need to create it.")

            

            # Check if 'new_question_command' exists in the table
            cursor.execute("SELECT new_question_prompt FROM my_table WHERE new_question_command = %s", (new_question_command,))
            existing_description = cursor.fetchone()
            if existing_description is not None:
                print("It EXISTS")
                new_question_prompt = existing_description[0]
                print(f"Exists {new_question_command} command for Question prompt: {new_question_prompt}")
            else:
                print("It DOES NOT EXIST")
                insert_data_query = "INSERT INTO my_table (new_question_command, new_question_prompt) VALUES (%s, %s) RETURNING new_question_prompt;"
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

    def timeout_handler():
        timeout_event.set()
        # print("Timer is set.")

    timer_thread = threading.Timer(timeout_seconds, timeout_handler)
    timer_thread.start()
    # time.sleep(3)
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






# def get_api_key():
#     connection = sqlite3.connect("config.db")
#     cursor = connection.cursor()

#     # Retrieve the API key from the database
#     cursor.execute("SELECT api_key FROM api_config WHERE id = 1")
#     api_key = cursor.fetchone()

#     connection.close()

#     return api_key[0] if api_key else None


# def insert_api_key(api_key):
#     connection = sqlite3.connect("config.db")
#     cursor = connection.cursor()

#     # Insert the API key into the database
#     cursor.execute("INSERT INTO api_config (api_key) VALUES (?)", (api_key,))
#     connection.commit()
#     connection.close()

# # Insert your API key into the database

# insert_api_key("a")


if __name__ == '__main__':
    # Start a thread for health checking
    health_check_thread = threading.Thread(target=check_health)
    health_check_thread.daemon = True
    health_check_thread.start()

    reset_thread = threading.Thread(target=reset_counter, daemon=True)

    reset_thread.start()
    # reset_thread.join()

    

    app.run(host="0.0.0.0", port=5000, debug=True)



# def load_service_config():
#     # Load service configuration from a JSON file
#     with open('replica.json', 'r') as json_file:
#         services_config = json.load(json_file)
#     return services_config

# def start_services(services_config):
#     for service_name, service_info in services_config.items():
#         service_port = random.choice(service_info['ports'])
#         print(f"Starting service '{service_name}' on port {service_port}...")
#         # Start your service with the specified service_name and service_port
#         # You can create a new Flask app and run it on the specified port
#         service_app = Flask(__name__)
#         service_app.run(host="0.0.0.0", port=service_port, debug=True)

# def start_server(service_name, port):
#     app.run(host="0.0.0.0", port=port, debug=True)

# def start_services(service_config):
#     service_name = list(service_config.keys())[0]  # Get the service name
#     ports = service_config[service_name].get("ports")
#     # for i in range(2):
#     if ports:
#         selected_port = random.choice(ports)
#         print(f"Starting {service_name} on port {selected_port}")
#         start_server(service_name, selected_port)

# def load_service_config():
#     with open('chat_gpt_service\service.json', 'r') as json_file:
#         service_config = json.load(json_file)
#         return service_config

# if __name__ == '__main__':
#     health_check_thread = threading.Thread(target=check_health)
#     health_check_thread.daemon = True
#     health_check_thread.start()

#     reset_thread = threading.Thread(target=reset_counter, daemon=True)
#     reset_thread.start()

#     # Load service configuration
#     services_config = load_service_config()

#     services = []

#     # Start services based on the configuration
#     for i in range(2):
#         # start_services(services_config)

#         service_thread = threading.Thread(target=start_services(services_config), daemon=True)
#         services.append(service_thread)
#     for service in services:
#         service.start()
        




# py chat_gpt_service\chat_gpt_service.py