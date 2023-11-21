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
                host="postgres-database1",
                # host="192.168.2.150",
                # port="5433",
                database="postgres-db1"
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
                host="postgres-database1",
                # host="192.168.2.150",
                # port="5433",
                database="postgres-db1"
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
                host="postgres-database1",
                # host="192.168.2.150",
                # port="5433",
                database="postgres-db1"
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
