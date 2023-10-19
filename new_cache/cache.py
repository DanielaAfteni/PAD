# from flask import Flask, request, jsonify
# from neo4j import GraphDatabase

# app = Flask(__name__)

# # Define a class to manage the cache using Neo4j
# class Neo4jCache:
#     def __init__(self, uri, user, password):
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))

#     def get_data(self, key):
#         with self._driver.session() as session:
#             result = session.read_transaction(self._get_data, key)
#             return result

#     @staticmethod
#     def _get_data(tx, key):
#         query = "MATCH (data:Cache {key: $key}) RETURN data.value AS value"
#         result = tx.run(query, key=key)
#         return result.single()

#     def set_data(self, key, value):
#         with self._driver.session() as session:
#             session.write_transaction(self._set_data, key, value)

#     @staticmethod
#     def _set_data(tx, key, value):
#         query = "MERGE (data:Cache {key: $key}) SET data.value = $value"
#         tx.run(query, key=key, value=value)

# # Initialize the Neo4jCache with your Neo4j database URI, username, and password
# neo4j_cache = Neo4jCache("bolt://localhost:7687", "neo4j", "password")

# @app.route('/cache/<key>', methods=['GET', 'POST'])
# def cache_handler(key):
#     if request.method == 'GET':
#         result = neo4j_cache.get_data(key)
#         if result:
#             return jsonify({key: result['value']})
#         else:
#             return jsonify({'message': 'Key not found'}), 404

#     elif request.method == 'POST':
#         data = request.get_json()
#         neo4j_cache.set_data(key, data)
#         return jsonify({'message': 'Data cached successfully'})

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

NEO4J_BASE_URL = "http://localhost:7474"  # Replace with your Neo4j server URL
NEO4J_USERNAME = "neo4j"              # Replace with your Neo4j username
NEO4J_PASSWORD = "password"              # Replace with your Neo4j password

@app.route('/cache/<key>', methods=['GET', 'POST'])
def cache_handler(key):
    if request.method == 'GET':
        response = get_data_from_neo4j(key)
        if response.status_code == 200:
            data = response.json()
            return jsonify({key: data['value']})
        else:
            return jsonify({'message': 'Key not found'}), 404

    elif request.method == 'POST':
        data = request.get_json()
        response = set_data_in_neo4j(key, data)
        if response.status_code == 200:
            return jsonify({'message': 'Data cached successfully'})
        else:
            return jsonify({'message': 'Failed to cache data'}), 500

def get_data_from_neo4j(key):
    url = f"{NEO4J_BASE_URL}/db/data/transaction/commit"
    headers = {"Content-Type": "application/json"}
    data = {
        "statements": [
            {
                "statement": f"MATCH (data:Cache {{key: '{key}'}}) RETURN data.value AS value",
            }
        ]
    }
    return requests.post(url, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), headers=headers, json=data)

def set_data_in_neo4j(key, data):
    url = f"{NEO4J_BASE_URL}/db/data/transaction/commit"
    headers = {"Content-Type": "application/json"}
    query = f"MATCH (data:Cache {{key: '{key}'}}) SET data.value = '{data}'"
    data = {
        "statements": [
            {
                "statement": query,
            }
        ]
    }
    return requests.post(url, auth=(NEO4J_USERNAME, NEO4J_PASSWORD), headers=headers, json=data)

if __name__ == '__main__':
    app.run(debug=True)