from flask import Flask, request, jsonify
from neo4j import GraphDatabase

app = Flask(__name__)

# Initialize an in-memory cache
cache = {}

# Define a class to interact with the Neo4j database
class Neo4jDB:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_node(self, key, value):
        with self._driver.session() as session:
            session.write_transaction(self._create_node, key, value)

    def delete_node(self, key):
        with self._driver.session() as session:
            session.write_transaction(self._delete_node, key)

    def get_node_value(self, key):
        with self._driver.session() as session:
            return session.read_transaction(self._get_node_value, key)

    @staticmethod
    def _create_node(tx, key, value):
        query = "CREATE (n:Node {key: $key, value: $value})"
        tx.run(query, key=key, value=value)

    @staticmethod
    def _delete_node(tx, key):
        query = "MATCH (n:Node {key: $key}) DELETE n"
        tx.run(query, key=key)

    @staticmethod
    def _get_node_value(tx, key):
        query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
        result = tx.run(query, key=key).single()
        if result:
            return result["value"]
        else:
            return None

# Set up the connection to the Neo4j database
neo4j_uri = "bolt://neo4j-database"
# neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"  # Replace with your actual password

db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

@app.route('/create_node', methods=['POST'])
def create_node():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')
    
    # Check if the data is in the cache
    if key in cache:
        result = cache[key]
        print("The data Exists")
    else:
        # If not in cache, create the node and add to the cache
        db.create_node(key, value)
        result = {"message": "Node created successfully"}
        cache[key] = result
    
    return jsonify(result)

@app.route('/delete_node', methods=['POST'])
def delete_node():
    data = request.get_json()
    key = data.get('key')
    
    if key in cache:
        del cache[key]  # Remove from cache
        db.delete_node(key)  # Delete the node in the database
        result = {"message": "Node deleted successfully"}
    else:
        result = {"message": "Node not found in cache"}
    
    return jsonify(result)

@app.route('/get_value', methods=['GET'])
def get_value():
    data = request.get_json()
    key = data.get('key')
    
    value = db.get_node_value(key)
    if value is not None:
        # result = {"key": key, "value": value}
        result = {"value": value}
    else:
        result = {"message": "Node not found with the given key"}
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
