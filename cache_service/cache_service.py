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

    def create_node(self, name):
        with self._driver.session() as session:
            session.write_transaction(self._create_node, name)

    @staticmethod
    def _create_node(tx, name):
        query = "CREATE (n:Node {name: $name})"
        tx.run(query, name=name)

# Set up the connection to the Neo4j database
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "password"  # Replace with your actual password

db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

@app.route('/create_node', methods=['POST'])
def create_node():
    data = request.get_json()
    name = data.get('name')
    
    # Check if the data is in the cache
    if name in cache:
        result = cache[name]
    else:
        # If not in cache, create the node and add to the cache
        db.create_node(name)
        result = {"message": "Node created successfully"}
        cache[name] = result
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
