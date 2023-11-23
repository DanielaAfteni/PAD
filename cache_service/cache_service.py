# # # # # # # # # # from flask import Flask, request, jsonify
# # # # # # # # # # from neo4j import GraphDatabase

# # # # # # # # # # app = Flask(__name__)

# # # # # # # # # # # Initialize an in-memory cache
# # # # # # # # # # cache = {}

# # # # # # # # # # # Define a class to interact with the Neo4j database
# # # # # # # # # # class Neo4jDB:
# # # # # # # # # #     def __init__(self, uri, user, password):
# # # # # # # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # # # # # # #     def close(self):
# # # # # # # # # #         self._driver.close()

# # # # # # # # # #     def create_node(self, key, value):
# # # # # # # # # #         with self._driver.session() as session:
# # # # # # # # # #             session.write_transaction(self._create_node, key, value)

# # # # # # # # # #     def delete_node(self, key):
# # # # # # # # # #         with self._driver.session() as session:
# # # # # # # # # #             session.write_transaction(self._delete_node, key)

# # # # # # # # # #     def get_node_value(self, key):
# # # # # # # # # #         with self._driver.session() as session:
# # # # # # # # # #             return session.read_transaction(self._get_node_value, key)

# # # # # # # # # #     @staticmethod
# # # # # # # # # #     def _create_node(tx, key, value):
# # # # # # # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # # # # # # #         tx.run(query, key=key, value=value)

# # # # # # # # # #     @staticmethod
# # # # # # # # # #     def _delete_node(tx, key):
# # # # # # # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # # # # # # #         tx.run(query, key=key)

# # # # # # # # # #     @staticmethod
# # # # # # # # # #     def _get_node_value(tx, key):
# # # # # # # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # # # # # # #         result = tx.run(query, key=key).single()
# # # # # # # # # #         if result:
# # # # # # # # # #             return result["value"]
# # # # # # # # # #         else:
# # # # # # # # # #             return None

# # # # # # # # # # # Set up the connection to the Neo4j database
# # # # # # # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # # # # # # neo4j_user = "neo4j"
# # # # # # # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # # # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # # # # # @app.route('/create_node', methods=['POST'])
# # # # # # # # # # def create_node():
# # # # # # # # # #     data = request.get_json()
# # # # # # # # # #     key = data.get('key')
# # # # # # # # # #     value = data.get('value')
    
# # # # # # # # # #     # Check if the data is in the cache
# # # # # # # # # #     if key in cache:
# # # # # # # # # #         result = cache[key]
# # # # # # # # # #         print("The data Exists")
# # # # # # # # # #     else:
# # # # # # # # # #         # If not in cache, create the node and add to the cache
# # # # # # # # # #         db.create_node(key, value)
# # # # # # # # # #         result = {"message": "Node created successfully"}
# # # # # # # # # #         cache[key] = result
    
# # # # # # # # # #     return jsonify(result)

# # # # # # # # # # @app.route('/delete_node', methods=['POST'])
# # # # # # # # # # def delete_node():
# # # # # # # # # #     data = request.get_json()
# # # # # # # # # #     key = data.get('key')
    
# # # # # # # # # #     if key in cache:
# # # # # # # # # #         del cache[key]  # Remove from cache
# # # # # # # # # #         db.delete_node(key)  # Delete the node in the database
# # # # # # # # # #         result = {"message": "Node deleted successfully"}
# # # # # # # # # #     else:
# # # # # # # # # #         result = {"message": "Node not found in cache"}
    
# # # # # # # # # #     return jsonify(result)

# # # # # # # # # # @app.route('/get_value', methods=['GET'])
# # # # # # # # # # def get_value():
# # # # # # # # # #     data = request.get_json()
# # # # # # # # # #     key = data.get('key')
    
# # # # # # # # # #     value = db.get_node_value(key)
# # # # # # # # # #     if value is not None:
# # # # # # # # # #         # result = {"key": key, "value": value}
# # # # # # # # # #         result = {"value": value}
# # # # # # # # # #     else:
# # # # # # # # # #         result = {"message": "Node not found with the given key"}
    
# # # # # # # # # #     return jsonify(result)

# # # # # # # # # # if __name__ == '__main__':
# # # # # # # # # #     app.run(host="0.0.0.0", port=4000, debug=True)



# # # # # # # # # from flask import Flask, request, jsonify
# # # # # # # # # from neo4j import GraphDatabase
# # # # # # # # # from hash_ring import HashRing

# # # # # # # # # app = Flask(__name__)

# # # # # # # # # # Define cache nodes and create a consistent hashing cache
# # # # # # # # # cache_nodes = {}
# # # # # # # # # replica_count = 3
# # # # # # # # # for i in range(replica_count):
# # # # # # # # #     node_name = f"Node-{i}"
# # # # # # # # #     cache_nodes[node_name] = {}
# # # # # # # # # cache_ring = HashRing(cache_nodes, replica_count=replica_count)

# # # # # # # # # # Define a class to interact with the Neo4j database
# # # # # # # # # class Neo4jDB:
# # # # # # # # #     def __init__(self, uri, user, password):
# # # # # # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # # # # # #     def close(self):
# # # # # # # # #         self._driver.close()

# # # # # # # # #     def create_node(self, key, value):
# # # # # # # # #         with self._driver.session() as session:
# # # # # # # # #             session.write_transaction(self._create_node, key, value)

# # # # # # # # #     def delete_node(self, key):
# # # # # # # # #         with self._driver.session() as session:
# # # # # # # # #             session.write_transaction(self._delete_node, key)

# # # # # # # # #     def get_node_value(self, key):
# # # # # # # # #         with self._driver.session() as session:
# # # # # # # # #             return session.read_transaction(self._get_node_value, key)

# # # # # # # # #     @staticmethod
# # # # # # # # #     def _create_node(tx, key, value):
# # # # # # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # # # # # #         tx.run(query, key=key, value=value)

# # # # # # # # #     @staticmethod
# # # # # # # # #     def _delete_node(tx, key):
# # # # # # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # # # # # #         tx.run(query, key=key)

# # # # # # # # #     @staticmethod
# # # # # # # # #     def _get_node_value(tx, key):
# # # # # # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # # # # # #         result = tx.run(query, key=key).single()
# # # # # # # # #         if result:
# # # # # # # # #             return result["value"]
# # # # # # # # #         else:
# # # # # # # # #             return None

# # # # # # # # # # Set up the connection to the Neo4j database
# # # # # # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # # # # # neo4j_user = "neo4j"
# # # # # # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # # # # @app.route('/create_node', methods=['POST'])
# # # # # # # # # def create_node():
# # # # # # # # #     data = request.get_json()
# # # # # # # # #     key = data.get('key')
# # # # # # # # #     value = data.get('value')

# # # # # # # # #     # Get the cache node using consistent hashing
# # # # # # # # #     node_name = cache_ring.get_node(key)

# # # # # # # # #     # Check if the data is in the cache
# # # # # # # # #     if key in cache_nodes[node_name]:
# # # # # # # # #         result = cache_nodes[node_name][key]
# # # # # # # # #         print("The data exists in cache")
# # # # # # # # #     else:
# # # # # # # # #         # If not in cache, create the node and add to the cache
# # # # # # # # #         db.create_node(key, value)
# # # # # # # # #         result = {"message": "Node created successfully"}

# # # # # # # # #         # Add to the cache
# # # # # # # # #         cache_nodes[node_name][key] = result

# # # # # # # # #     return jsonify(result)

# # # # # # # # # @app.route('/delete_node', methods=['POST'])
# # # # # # # # # def delete_node():
# # # # # # # # #     data = request.get_json()
# # # # # # # # #     key = data.get('key')

# # # # # # # # #     # Get the cache node using consistent hashing
# # # # # # # # #     node_name = cache_ring.get_node(key)

# # # # # # # # #     if key in cache_nodes[node_name]:
# # # # # # # # #         del cache_nodes[node_name][key]  # Remove from cache
# # # # # # # # #         db.delete_node(key)  # Delete the node in the database
# # # # # # # # #         result = {"message": "Node deleted successfully"}
# # # # # # # # #     else:
# # # # # # # # #         result = {"message": "Node not found in cache"}

# # # # # # # # #     return jsonify(result)

# # # # # # # # # @app.route('/get_value', methods=['GET'])
# # # # # # # # # def get_value():
# # # # # # # # #     data = request.get_json()
# # # # # # # # #     key = data.get('key')

# # # # # # # # #     # Get the cache node using consistent hashing
# # # # # # # # #     node_name = cache_ring.get_node(key)

# # # # # # # # #     value = db.get_node_value(key)
# # # # # # # # #     if value is not None:
# # # # # # # # #         # result = {"key": key, "value": value}
# # # # # # # # #         result = {"value": value}
# # # # # # # # #     else:
# # # # # # # # #         result = {"message": "Node not found with the given key"}

# # # # # # # # #     return jsonify(result)

# # # # # # # # # if __name__ == '__main__':
# # # # # # # # #     app.run(host="0.0.0.0", port=4000, debug=True)



# # # # # # # # from flask import Flask, request, jsonify
# # # # # # # # from neo4j import GraphDatabase
# # # # # # # # from cachetools import LRUCache, hashkey, hash_ring

# # # # # # # # app = Flask(__name__)

# # # # # # # # # Create cache nodes with the given replica_count
# # # # # # # # replica_count = 3
# # # # # # # # cache_nodes = {}
# # # # # # # # for i in range(replica_count):
# # # # # # # #     node_name = f"Node-{i}"
# # # # # # # #     cache_nodes[node_name] = LRUCache(maxsize=1000)


# # # # # # # # # Create a hash ring with the nodes
# # # # # # # # ring = hash_ring.HashRing(nodes=cache_nodes.keys())


# # # # # # # # # Define a class to interact with the Neo4j database
# # # # # # # # class Neo4jDB:
# # # # # # # #     def __init__(self, uri, user, password):
# # # # # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # # # # #     def close(self):
# # # # # # # #         self._driver.close()

# # # # # # # #     def create_node(self, key, value):
# # # # # # # #         with self._driver.session() as session:
# # # # # # # #             session.write_transaction(self._create_node, key, value)

# # # # # # # #     def delete_node(self, key):
# # # # # # # #         with self._driver.session() as session:
# # # # # # # #             session.write_transaction(self._delete_node, key)

# # # # # # # #     def get_node_value(self, key):
# # # # # # # #         with self._driver.session() as session:
# # # # # # # #             return session.read_transaction(self._get_node_value, key)

# # # # # # # #     @staticmethod
# # # # # # # #     def _create_node(tx, key, value):
# # # # # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # # # # #         tx.run(query, key=key, value=value)

# # # # # # # #     @staticmethod
# # # # # # # #     def _delete_node(tx, key):
# # # # # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # # # # #         tx.run(query, key=key)

# # # # # # # #     @staticmethod
# # # # # # # #     def _get_node_value(tx, key):
# # # # # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # # # # #         result = tx.run(query, key=key).single()
# # # # # # # #         if result:
# # # # # # # #             return result["value"]
# # # # # # # #         else:
# # # # # # # #             return None

# # # # # # # # # Set up the connection to the Neo4j database
# # # # # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # # # # neo4j_user = "neo4j"
# # # # # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # # # @app.route('/create_node', methods=['POST'])
# # # # # # # # def create_node():
# # # # # # # #     data = request.get_json()
# # # # # # # #     key = data.get('key')
# # # # # # # #     value = data.get('value')

# # # # # # # #     # Get the cache node using the ring
# # # # # # # #     node_name = ring.get_node(key)

# # # # # # # #     # Check if the data is in the cache
# # # # # # # #     if key in cache_nodes[node_name]:
# # # # # # # #         result = cache_nodes[node_name][key]
# # # # # # # #         print("The data exists in cache")
# # # # # # # #     else:
# # # # # # # #         # If not in cache, create the node and add to the cache
# # # # # # # #         db.create_node(key, value)
# # # # # # # #         result = {"message": "Node created successfully"}

# # # # # # # #         # Add to the cache
# # # # # # # #         cache_nodes[node_name][key] = result

# # # # # # # #     return jsonify(result)

# # # # # # # # @app.route('/delete_node', methods=['POST'])
# # # # # # # # def delete_node():
# # # # # # # #     data = request.get_json()
# # # # # # # #     key = data.get('key')

# # # # # # # #     # Get the cache node using the ring
# # # # # # # #     node_name = ring.get_node(key)

# # # # # # # #     if key in cache_nodes[node_name]:
# # # # # # # #         del cache_nodes[node_name][key]  # Remove from cache
# # # # # # # #         db.delete_node(key)  # Delete the node in the database
# # # # # # # #         result = {"message": "Node deleted successfully"}
# # # # # # # #     else:
# # # # # # # #         result = {"message": "Node not found in cache"}

# # # # # # # #     return jsonify(result)

# # # # # # # # @app.route('/get_value', methods=['GET'])
# # # # # # # # def get_value():
# # # # # # # #     data = request.get_json()
# # # # # # # #     key = data.get('key')

# # # # # # # #     # Get the cache node using the ring
# # # # # # # #     node_name = ring.get_node(key)

# # # # # # # #     value = db.get_node_value(key)
# # # # # # # #     if value is not None:
# # # # # # # #         result = {"value": value}
# # # # # # # #     else:
# # # # # # # #         result = {"message": "Node not found with the given key"}

# # # # # # # #     return jsonify(result)

# # # # # # # # if __name__ == '__main__':
# # # # # # # #     app.run(host="0.0.0.0", port=4000, debug=True)

# # # # # # # from flask import Flask, request, jsonify
# # # # # # # from neo4j import GraphDatabase
# # # # # # # from cachetools import LRUCache
# # # # # # # from cachetools.keys import hashkey
# # # # # # # from cachetools import hash_ring

# # # # # # # app = Flask(__name__)

# # # # # # # # Create cache nodes with the given replica_count
# # # # # # # replica_count = 3
# # # # # # # cache_nodes = {}
# # # # # # # for i in range(replica_count):
# # # # # # #     node_name = f"Node-{i}"
# # # # # # #     cache_nodes[node_name] = LRUCache(maxsize=1000)

# # # # # # # # Create a hash ring with the nodes
# # # # # # # ring = hash_ring.HashRing(cache_nodes.keys(), hash_fn=hashkey)

# # # # # # # # Define a class to interact with the Neo4j database
# # # # # # # class Neo4jDB:
# # # # # # #     def __init__(self, uri, user, password):
# # # # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # # # #     def close(self):
# # # # # # #         self._driver.close()

# # # # # # #     def create_node(self, key, value):
# # # # # # #         with self._driver.session() as session:
# # # # # # #             session.write_transaction(self._create_node, key, value)

# # # # # # #     def delete_node(self, key):
# # # # # # #         with self._driver.session() as session:
# # # # # # #             session.write_transaction(self._delete_node, key)

# # # # # # #     def get_node_value(self, key):
# # # # # # #         with self._driver.session() as session:
# # # # # # #             return session.read_transaction(self._get_node_value, key)

# # # # # # #     @staticmethod
# # # # # # #     def _create_node(tx, key, value):
# # # # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # # # #         tx.run(query, key=key, value=value)

# # # # # # #     @staticmethod
# # # # # # #     def _delete_node(tx, key):
# # # # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # # # #         tx.run(query, key=key)

# # # # # # #     @staticmethod
# # # # # # #     def _get_node_value(tx, key):
# # # # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # # # #         result = tx.run(query, key=key).single()
# # # # # # #         if result:
# # # # # # #             return result["value"]
# # # # # # #         else:
# # # # # # #             return None
        
# # # # # # # # Set up the connection to the Neo4j database
# # # # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # # # neo4j_user = "neo4j"
# # # # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # # @app.route('/create_node', methods=['POST'])
# # # # # # # def create_node():
# # # # # # #     data = request.get_json()
# # # # # # #     key = data.get('key')
# # # # # # #     value = data.get('value')

# # # # # # #     # Get the cache node using the ring
# # # # # # #     node_name = ring.get_node(key)

# # # # # # #     # Check if the data is in the cache
# # # # # # #     if key in cache_nodes[node_name]:
# # # # # # #         result = cache_nodes[node_name][key]
# # # # # # #         print("The data exists in cache")
# # # # # # #     else:
# # # # # # #         # If not in cache, create the node and add to the cache
# # # # # # #         db.create_node(key, value)
# # # # # # #         result = {"message": "Node created successfully"}

# # # # # # #         # Add to the cache
# # # # # # #         cache_nodes[node_name][key] = result

# # # # # # #     return jsonify(result)

# # # # # # # @app.route('/delete_node', methods=['POST'])
# # # # # # # def delete_node():
# # # # # # #     data = request.get_json()
# # # # # # #     key = data.get('key')

# # # # # # #     # Get the cache node using the ring
# # # # # # #     node_name = ring.get_node(key)

# # # # # # #     if key in cache_nodes[node_name]:
# # # # # # #         del cache_nodes[node_name][key]  # Remove from cache
# # # # # # #         db.delete_node(key)  # Delete the node in the database
# # # # # # #         result = {"message": "Node deleted successfully"}
# # # # # # #     else:
# # # # # # #         result = {"message": "Node not found in cache"}

# # # # # # #     return jsonify(result)

# # # # # # # @app.route('/get_value', methods=['GET'])
# # # # # # # def get_value():
# # # # # # #     data = request.get_json()
# # # # # # #     key = data.get('key')

# # # # # # #     # Get the cache node using the ring
# # # # # # #     node_name = ring.get_node(key)

# # # # # # #     value = db.get_node_value(key)
# # # # # # #     if value is not None:
# # # # # # #         result = {"value": value}
# # # # # # #     else:
# # # # # # #         result = {"message": "Node not found with the given key"}

# # # # # # #     return jsonify(result)

# # # # # # # if __name__ == '__main__':
# # # # # # #     app.run(host="0.0.0.0", port=4000, debug=True)


# # # # # # from flask import Flask, request, jsonify
# # # # # # from neo4j import GraphDatabase
# # # # # # from hash_ring import HashRing

# # # # # # app = Flask(__name__)

# # # # # # # Create a cache ring with the nodes
# # # # # # replica_count = 3
# # # # # # cache_nodes = {}
# # # # # # for i in range(replica_count):
# # # # # #     node_name = f"Node-{i}"
# # # # # #     cache_nodes[node_name] = {}

# # # # # # cache_ring = HashRing(cache_nodes, replica_count=replica_count)

# # # # # # # Define a class to interact with the Neo4j database
# # # # # # class Neo4jDB:
# # # # # #     def __init__(self, uri, user, password):
# # # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # # #     def close(self):
# # # # # #         self._driver.close()

# # # # # #     def create_node(self, key, value):
# # # # # #         with self._driver.session() as session:
# # # # # #             session.write_transaction(self._create_node, key, value)

# # # # # #     def delete_node(self, key):
# # # # # #         with self._driver.session() as session:
# # # # # #             session.write_transaction(self._delete_node, key)

# # # # # #     def get_node_value(self, key):
# # # # # #         with self._driver.session() as session:
# # # # # #             return session.read_transaction(self._get_node_value, key)

# # # # # #     @staticmethod
# # # # # #     def _create_node(tx, key, value):
# # # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # # #         tx.run(query, key=key, value=value)

# # # # # #     @staticmethod
# # # # # #     def _delete_node(tx, key):
# # # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # # #         tx.run(query, key=key)

# # # # # #     @staticmethod
# # # # # #     def _get_node_value(tx, key):
# # # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # # #         result = tx.run(query, key=key).single()
# # # # # #         if result:
# # # # # #             return result["value"]
# # # # # #         else:
# # # # # #             return None

# # # # # # # Set up the connection to the Neo4j database
# # # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # # neo4j_user = "neo4j"
# # # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # @app.route('/create_node', methods=['POST'])
# # # # # # def create_node():
# # # # # #     data = request.get_json()
# # # # # #     key = data.get('key')
# # # # # #     value = data.get('value')

# # # # # #     # Get the cache node using consistent hashing
# # # # # #     node_name = cache_ring.get_node(key)

# # # # # #     # Check if the data is in the cache
# # # # # #     if key in cache_nodes[node_name]:
# # # # # #         result = cache_nodes[node_name][key]
# # # # # #         print("The data exists in cache")
# # # # # #     else:
# # # # # #         # If not in cache, create the node and add to the cache
# # # # # #         db.create_node(key, value)
# # # # # #         result = {"message": "Node created successfully"}

# # # # # #         # Add to the cache
# # # # # #         cache_nodes[node_name][key] = result

# # # # # #     return jsonify(result)

# # # # # # @app.route('/delete_node', methods=['POST'])
# # # # # # def delete_node():
# # # # # #     data = request.get_json()
# # # # # #     key = data.get('key')

# # # # # #     # Get the cache node using consistent hashing
# # # # # #     node_name = cache_ring.get_node(key)

# # # # # #     if key in cache_nodes[node_name]:
# # # # # #         del cache_nodes[node_name][key]  # Remove from cache
# # # # # #         db.delete_node(key)  # Delete the node in the database
# # # # # #         result = {"message": "Node deleted successfully"}
# # # # # #     else:
# # # # # #         result = {"message": "Node not found in cache"}

# # # # # #     return jsonify(result)

# # # # # # @app.route('/get_value', methods=['GET'])
# # # # # # def get_value():
# # # # # #     data = request.get_json()
# # # # # #     key = data.get('key')

# # # # # #     # Get the cache node using consistent hashing
# # # # # #     node_name = cache_ring.get_node(key)

# # # # # #     value = db.get_node_value(key)
# # # # # #     if value is not None:
# # # # # #         result = {"value": value}
# # # # # #     else:
# # # # # #         result = {"message": "Node not found with the given key"}

# # # # # #     return jsonify(result)

# # # # # # if __name__ == '__main__':
# # # # # #     app.run(host="0.0.0.0", port=4000, debug=True)


# # # # # from flask import Flask, request, jsonify
# # # # # from neo4j import GraphDatabase
# # # # # from ketama import KetamaRing

# # # # # app = Flask(__name__)

# # # # # # Create a cache ring with the nodes
# # # # # replica_count = 3
# # # # # cache_nodes = {}
# # # # # for i in range(replica_count):
# # # # #     node_name = f"Node-{i}"
# # # # #     cache_nodes[node_name] = {}

# # # # # # Create a hash ring with the nodes
# # # # # cache_ring = KetamaRing(cache_nodes)

# # # # # # Define a class to interact with the Neo4j database
# # # # # class Neo4jDB:
# # # # #     def __init__(self, uri, user, password):
# # # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # # #     def close(self):
# # # # #         self._driver.close()

# # # # #     def create_node(self, key, value):
# # # # #         with self._driver.session() as session:
# # # # #             session.write_transaction(self._create_node, key, value)

# # # # #     def delete_node(self, key):
# # # # #         with self._driver.session() as session:
# # # # #             session.write_transaction(self._delete_node, key)

# # # # #     def get_node_value(self, key):
# # # # #         with self._driver.session() as session:
# # # # #             return session.read_transaction(self._get_node_value, key)

# # # # #     @staticmethod
# # # # #     def _create_node(tx, key, value):
# # # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # # #         tx.run(query, key=key, value=value)

# # # # #     @staticmethod
# # # # #     def _delete_node(tx, key):
# # # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # # #         tx.run(query, key=key)

# # # # #     @staticmethod
# # # # #     def _get_node_value(tx, key):
# # # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # # #         result = tx.run(query, key=key).single()
# # # # #         if result:
# # # # #             return result["value"]
# # # # #         else:
# # # # #             return None

# # # # # # Set up the connection to the Neo4j database
# # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # neo4j_user = "neo4j"
# # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # # Set up the connection to the Neo4j database
# # # # # neo4j_uri = "bolt://neo4j-database"
# # # # # # neo4j_uri = "bolt://localhost:7687"
# # # # # neo4j_user = "neo4j"
# # # # # neo4j_password = "password"  # Replace with your actual password

# # # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # @app.route('/create_node', methods=['POST'])
# # # # # def create_node():
# # # # #     data = request.get_json()
# # # # #     key = data.get('key')
# # # # #     value = data.get('value')

# # # # #     # Get the cache node using consistent hashing
# # # # #     node_name = cache_ring.get_node(key)

# # # # #     # Check if the data is in the cache
# # # # #     if key in cache_nodes[node_name]:
# # # # #         result = cache_nodes[node_name][key]
# # # # #         print("The data exists in cache")
# # # # #     else:
# # # # #         # If not in cache, create the node and add to the cache
# # # # #         db.create_node(key, value)
# # # # #         result = {"message": "Node created successfully"}

# # # # #         # Add to the cache
# # # # #         cache_nodes[node_name][key] = result

# # # # #     return jsonify(result)

# # # # # @app.route('/delete_node', methods=['POST'])
# # # # # def delete_node():
# # # # #     data = request.get_json()
# # # # #     key = data.get('key')

# # # # #     # Get the cache node using consistent hashing
# # # # #     node_name = cache_ring.get_node(key)

# # # # #     if key in cache_nodes[node_name]:
# # # # #         del cache_nodes[node_name][key]  # Remove from cache
# # # # #         db.delete_node(key)  # Delete the node in the database
# # # # #         result = {"message": "Node deleted successfully"}
# # # # #     else:
# # # # #         result = {"message": "Node not found in cache"}

# # # # #     return jsonify(result)

# # # # # @app.route('/get_value', methods=['GET'])
# # # # # def get_value():
# # # # #     data = request.get_json()
# # # # #     key = data.get('key')

# # # # #     # Get the cache node using consistent hashing
# # # # #     node_name = cache_ring.get_node(key)

# # # # #     value = db.get_node_value(key)
# # # # #     if value is not None:
# # # # #         result = {"value": value}
# # # # #     else:
# # # # #         result = {"message": "Node not found with the given key"}

# # # # #     return jsonify(result)

# # # # # if __name__ == '__main__':
# # # # #     app.run(host="0.0.0.0", port=4000, debug=True)

# # # # from flask import Flask, request, jsonify
# # # # from neo4j import GraphDatabase
# # # # import memcache
# # # # import logging

# # # # # Configure the logging module
# # # # logging.basicConfig(level=logging.INFO)
# # # # logger = logging.getLogger(__name__)


# # # # app = Flask(__name__)

# # # # # Create a list of cache nodes
# # # # replica_count = 3
# # # # # cache_nodes = []
# # # # # for i in range(replica_count):
# # # # #     node_name = f"Node-{i}"
# # # # #     cache_nodes.append(node_name)

# # # # cache_nodes = ["127.0.0.1", "192.168.0.2", "10.0.0.3"]


# # # # # Create a memcached client with consistent hashing
# # # # # cache_client = pylibmc.Client(cache_nodes, binary=True)

# # # # cache_client = memcache.Client(cache_nodes)

# # # # # Define a class to interact with the Neo4j database
# # # # class Neo4jDB:
# # # #     def __init__(self, uri, user, password):
# # # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # # #     def close(self):
# # # #         self._driver.close()

# # # #     def create_node(self, key, value):
# # # #         with self._driver.session() as session:
# # # #             session.write_transaction(self._create_node, key, value)

# # # #     def delete_node(self, key):
# # # #         with self._driver.session() as session:
# # # #             session.write_transaction(self._delete_node, key)

# # # #     def get_node_value(self, key):
# # # #         with self._driver.session() as session:
# # # #             return session.read_transaction(self._get_node_value, key)

# # # #     @staticmethod
# # # #     def _create_node(tx, key, value):
# # # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # # #         tx.run(query, key=key, value=value)

# # # #     @staticmethod
# # # #     def _delete_node(tx, key):
# # # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # # #         tx.run(query, key=key)

# # # #     @staticmethod
# # # #     def _get_node_value(tx, key):
# # # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # # #         result = tx.run(query, key=key).single()
# # # #         if result:
# # # #             return result["value"]
# # # #         else:
# # # #             return None
        
# # # # # Set up the connection to the Neo4j database
# # # # neo4j_uri = "bolt://neo4j-database"
# # # # # neo4j_uri = "bolt://localhost:7687"
# # # # neo4j_user = "neo4j"
# # # # neo4j_password = "password"  # Replace with your actual password

# # # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # # # @app.route('/create_node', methods=['POST'])
# # # # # def create_node():
# # # # #     data = request.get_json()
# # # # #     key = data.get('key')
# # # # #     value = data.get('value')

# # # # #     # Get the cache node using consistent hashing
# # # # #     node_name = cache_client.get(key)

# # # # #     # Log the cache node involved in the process
# # # # #     logger.info("Creating node for key: %s on cache node: %s", key, node_name)

# # # # #     # Check if the data is in the cache
# # # # #     cached_value = cache_client.get(key)
# # # # #     if cached_value is not None:
# # # # #         result = cached_value
# # # # #         print("The data exists in cache")
# # # # #         logger.info("Data exists in cache for key: %s on cache node: %s", key, node_name) 
# # # # #     else:
# # # # #         # If not in cache, create the node and add to the cache
# # # # #         db.create_node(key, value)
# # # # #         result = {"message": "Node created successfully"}

# # # # #         # Add to the cache with a specific node as the key
# # # # #         cache_client.set(key, result, time=3600, key=node_name)
# # # # #         logger.info("Data added to cache for key: %s on cache node: %s", key, node_name)

# # # # #     return jsonify(result)

# # # # @app.route('/create_node', methods=['POST'])
# # # # def create_node():
# # # #     data = request.get_json()
# # # #     key = data.get('key')
# # # #     value = data.get('value')

# # # #     # Get the cache node using consistent hashing
# # # #     node_name = cache_client.get(key)

# # # #     # Log the cache node involved in the process
# # # #     logger.info("Creating node for key: %s on cache node: %s", key, node_name)

# # # #     # Check if the data is in the cache
# # # #     cached_value = cache_client.get(key)
# # # #     if cached_value is not None:
# # # #         result = cached_value
# # # #         logger.info("Data exists in cache for key: %s on cache node: %s", key, node_name)
# # # #     else:
# # # #         # If not in cache, create the node and add to the cache
# # # #         db.create_node(key, value)
# # # #         result = {"message": "Node created successfully"}

# # # #         # Add to the cache with a specific node as the key
# # # #         cache_client.set(key, result, time=3600)
# # # #         logger.info("Data added to cache for key: %s on cache node: %s", key, node_name)

# # # #     return jsonify(result)

# # # # @app.route('/delete_node', methods=['POST'])
# # # # def delete_node():
# # # #     data = request.get_json()
# # # #     key = data.get('key')

# # # #     # Get the cache node using consistent hashing
# # # #     node_name = cache_client.get(key)

# # # #     logger.info("Deleting node for key: %s on cache node: %s", key, node_name)

# # # #     if key in cache_client:
# # # #         cache_client.delete(key)  # Remove from cache
# # # #         db.delete_node(key)  # Delete the node in the database
# # # #         result = {"message": "Node deleted successfully"}
# # # #         logger.info("Node deleted from cache and database for key: %s on cache node: %s", key, node_name)
# # # #     else:
# # # #         result = {"message": "Node not found in cache"}
# # # #         logger.info("Node not found in cache for key: %s on cache node: %s", key, node_name) 

# # # #     return jsonify(result)

# # # # @app.route('/get_value', methods=['GET'])
# # # # def get_value():
# # # #     data = request.get_json()
# # # #     key = data.get('key')

# # # #     # Get the cache node using consistent hashing
# # # #     node_name = cache_client.get(key)

# # # #     logger.info("Getting value for key: %s from cache node: %s", key, node_name)

# # # #     cached_value = cache_client.get(key)
# # # #     if cached_value is not None:
# # # #         result = cached_value
# # # #         print("The data exists in cache")
# # # #         logger.info("Data retrieved from cache for key: %s on cache node: %s", key, node_name)
# # # #     else:
# # # #         value = db.get_node_value(key)
# # # #         if value is not None:
# # # #             result = value
# # # #             cache_client.set(key, value, time=3600, key=node_name)
# # # #             logger.info("Data retrieved from database and added to cache for key: %s on cache node: %s", key, node_name)
# # # #         else:
# # # #             result = {"message": "Node not found with the given key"}
# # # #             logger.info("Node not found in cache and database for key: %s on cache node: %s", key, node_name)

# # # #     return jsonify(result)

# # # # if __name__ == '__main__':
# # # #     app.run(host="0.0.0.0", port=4000, debug=True)



# # # from flask import Flask, request, jsonify
# # # from neo4j import GraphDatabase
# # # import memcache
# # # import logging

# # # # Configure the logging module
# # # logging.basicConfig(level=logging.INFO)
# # # logger = logging.getLogger(__name__)

# # # app = Flask(__name__)

# # # # Create a list of cache nodes
# # # replica_count = 3
# # # cache_nodes = ["127.0.0.1:11211", "192.168.0.2:11211", "10.0.0.3:11211"]

# # # # Create a memcached client with consistent hashing
# # # cache_client = memcache.Client(cache_nodes)

# # # # Define a class to interact with the Neo4j database
# # # class Neo4jDB:
# # #     def __init__(self, uri, user, password):
# # #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# # #     def close(self):
# # #         self._driver.close()

# # #     def create_node(self, key, value):
# # #         with self._driver.session() as session:
# # #             session.write_transaction(self._create_node, key, value)

# # #     def delete_node(self, key):
# # #         with self._driver.session() as session:
# # #             session.write_transaction(self._delete_node, key)

# # #     def get_node_value(self, key):
# # #         with self._driver.session() as session:
# # #             return session.read_transaction(self._get_node_value, key)

# # #     @staticmethod
# # #     def _create_node(tx, key, value):
# # #         query = "CREATE (n:Node {key: $key, value: $value})"
# # #         tx.run(query, key=key, value=value)

# # #     @staticmethod
# # #     def _delete_node(tx, key):
# # #         query = "MATCH (n:Node {key: $key}) DELETE n"
# # #         tx.run(query, key=key)

# # #     @staticmethod
# # #     def _get_node_value(tx, key):
# # #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# # #         result = tx.run(query, key=key).single()
# # #         if result:
# # #             return result["value"]
# # #         else:
# # #             return None

# # # # Set up the connection to the Neo4j database
# # # neo4j_uri = "bolt://neo4j-database"
# # # neo4j_user = "neo4j"
# # # neo4j_password = "password"  # Replace with your actual password

# # # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # # @app.route('/create_node', methods=['POST'])
# # # def create_node():
# # #     data = request.get_json()
# # #     key = data.get('key')
# # #     value = data.get('value')

# # #     # Log the cache node involved in the process
# # #     logger.info("Creating node for key: %s", key)

# # #     # Check if the data is in the cache
# # #     cached_value = cache_client.get(key)
# # #     if cached_value is not None:
# # #         result = cached_value
# # #         logger.info("Data exists in cache for key: %s", key)
# # #     else:
# # #         # If not in cache, create the node and add to the cache
# # #         db.create_node(key, value)
# # #         result = {"message": "Node created successfully"}

# # #         # Add to the cache
# # #         cache_client.set(key, result, time=3600)
# # #         logger.info("Data added to cache for key: %s", key)

# # #     return jsonify(result)

# # # @app.route('/delete_node', methods=['POST'])
# # # def delete_node():
# # #     data = request.get_json()
# # #     key = data.get('key')

# # #     # Log the cache node involved in the process
# # #     logger.info("Deleting node for key: %s", key)

# # #     if key in cache_client:
# # #         cache_client.delete(key)  # Remove from cache
# # #         db.delete_node(key)  # Delete the node in the database
# # #         result = {"message": "Node deleted successfully"}
# # #         logger.info("Node deleted from cache and database for key: %s", key)
# # #     else:
# # #         result = {"message": "Node not found in cache"}
# # #         logger.info("Node not found in cache for key: %s", key)

# # #     return jsonify(result)

# # # @app.route('/get_value', methods=['GET'])
# # # def get_value():
# # #     data = request.get_json()
# # #     key = data.get('key')

# # #     # Log the cache node involved in the process
# # #     logger.info("Getting value for key: %s", key)

# # #     cached_value = cache_client.get(key)
# # #     if cached_value is not None:
# # #         result = cached_value
# # #         logger.info("Data retrieved from cache for key: %s", key)
# # #     else:
# # #         value = db.get_node_value(key)
# # #         if value is not None:
# # #             result = value
# # #             cache_client.set(key, value, time=3600)
# # #             logger.info("Data retrieved from database and added to cache for key: %s", key)
# # #         else:
# # #             result = {"message": "Node not found with the given key"}
# # #             logger.info("Node not found in cache and database for key: %s", key)

# # #     return jsonify(result)

# # # if __name__ == '__main__':
# # #     app.run(host="0.0.0.0", port=4000, debug=True)


# # from flask import Flask, request, jsonify
# # from neo4j import GraphDatabase
# # import pylibmc  # Import the pylibmc library for consistent hashing
# # import logging

# # # Configure the logging module
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = Flask(__name__)

# # # Create a list of cache nodes
# # cache_nodes = ["127.0.0.1", "192.168.0.2", "10.0.0.3"]

# # # Create a pylibmc client with consistent hashing
# # # cache_client = pylibmc.Client(cache_nodes, binary=True, behaviors={"ketama": True})

# # try:
# #     cache_client = pylibmc.Client(cache_nodes, binary=True, behaviors={"ketama": True})
# #     logger.info("Cache client connected successfully.")
# # except Exception as e:
# #     logger.error("Cache client connection error: %s", e)
# #     raise e



# # # Define a class to interact with the Neo4j database
# # class Neo4jDB:
# #     def __init__(self, uri, user, password):
# #         self._driver = GraphDatabase.driver(uri, auth=(user, password))

# #     def close(self):
# #         self._driver.close()

# #     def create_node(self, key, value):
# #         with self._driver.session() as session:
# #             session.write_transaction(self._create_node, key, value)

# #     def delete_node(self, key):
# #         with self._driver.session() as session:
# #             session.write_transaction(self._delete_node, key)

# #     def get_node_value(self, key):
# #         with self._driver.session() as session:
# #             return session.read_transaction(self._get_node_value, key)

# #     @staticmethod
# #     def _create_node(tx, key, value):
# #         query = "CREATE (n:Node {key: $key, value: $value})"
# #         tx.run(query, key=key, value=value)

# #     @staticmethod
# #     def _delete_node(tx, key):
# #         query = "MATCH (n:Node {key: $key}) DELETE n"
# #         tx.run(query, key=key)

# #     @staticmethod
# #     def _get_node_value(tx, key):
# #         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
# #         result = tx.run(query, key=key).single()
# #         if result:
# #             return result["value"]
# #         else:
# #             return None

# # # Set up the connection to the Neo4j database
# # neo4j_uri = "bolt://neo4j-database"
# # # neo4j_uri = "bolt://localhost:7687"
# # neo4j_user = "neo4j"
# # neo4j_password = "password"  # Replace with your actual password

# # db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # @app.route('/create_node', methods=['POST'])
# # def create_node():
# #     data = request.get_json()
# #     key = data.get('key')
# #     value = data.get('value')

# #     # Log the cache node involved in the process
# #     logger.info("Creating node for key: %s", key)

# #     # Check if the data is in the cache
# #     cached_value = cache_client.get(key)
# #     if cached_value is not None:
# #         result = cached_value
# #         logger.info("Data exists in cache for key: %s", key)
# #     else:
# #         # If not in cache, create the node and add to the cache
# #         db.create_node(key, value)
# #         result = {"message": "Node created successfully"}

# #         # Add to the cache
# #         cache_client.set(key, result, time=3600)
# #         logger.info("Data added to cache for key: %s", key)

# #     return jsonify(result)

# # @app.route('/delete_node', methods=['POST'])
# # def delete_node():
# #     data = request.get_json()
# #     key = data.get('key')

# #     # Log the cache node involved in the process
# #     logger.info("Deleting node for key: %s", key)

# #     if key in cache_client:
# #         cache_client.delete(key)  # Remove from cache
# #         db.delete_node(key)  # Delete the node in the database
# #         result = {"message": "Node deleted successfully"}
# #         logger.info("Node deleted from cache and database for key: %s", key)
# #     else:
# #         result = {"message": "Node not found in cache"}
# #         logger.info("Node not found in cache for key: %s", key)

# #     return jsonify(result)

# # @app.route('/get_value', methods=['GET'])
# # def get_value():
# #     data = request.get_json()
# #     key = data.get('key')

# #     # Log the cache node involved in the process
# #     logger.info("Getting value for key: %s", key)

# #     cached_value = cache_client.get(key)
# #     if cached_value is not None:
# #         result = cached_value
# #         logger.info("Data retrieved from cache for key: %s", key)
# #     else:
# #         value = db.get_node_value(key)
# #         if value is not None:
# #             result = value
# #             cache_client.set(key, value, time=3600)
# #             logger.info("Data retrieved from database and added to cache for key: %s", key)
# #         else:
# #             result = {"message": "Node not found with the given key"}
# #             logger.info("Node not found in cache and database for key: %s", key)

# #     return jsonify(result)

# # if __name__ == '__main__':
# #     app.run(host="0.0.0.0", port=4000, debug=True)

# # from flask import Flask, request, jsonify
# # from neo4j import GraphDatabase
# # import pylibmc
# # import logging

# # # Configure the logging module
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = Flask(__name__)

# # # Create a list of cache nodes
# # replica_count = 3
# # cache_nodes = []
# # for i in range(replica_count):
# #     node_name = f"Node-{i}"
# #     cache_nodes.append(node_name)

# # # Adjust cache client initialization for consistent hashing with ketama
# # try:
# #     cache_client = pylibmc.Client(
# #         cache_nodes,
# #         binary=True,
# #         behaviors={"ketama": True},
# #     )
# #     logger.info("Cache client connected successfully.")
# # except Exception as e:
# #     logger.error("Cache client connection error: %s", e)
# #     raise e

# from flask import Flask, request, jsonify
# from neo4j import GraphDatabase
# import pylibmc
# import logging

# # Configure the logging module
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = Flask(__name__)

# # Create a list of cache nodes
# replica_count = 3
# cache_nodes = []
# for i in range(replica_count):
#     node_name = f"Node-{i}"
#     cache_nodes.append(node_name)

# # Adjust cache client initialization for consistent hashing with ketama
# try:
#     cache_client = pylibmc.Client(
#         cache_nodes,
#         binary=True,
#         behaviors={
#             "ketama": True,
#             "tcp_nodelay": True,
#             "no_block": True
#         }
#     )
#     logger.info("Cache client connected successfully.")
# except pylibmc.HostLookupError as hle:
#     logger.error("Host lookup error: %s", hle)
# except Exception as e:
#     logger.error("Cache client connection error: %s", e)
#     raise e


# # Define a class to interact with the Neo4j database
# class Neo4jDB:
#     def __init__(self, uri, user, password):
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self._driver.close()

#     def create_node(self, key, value):
#         with self._driver.session() as session:
#             session.write_transaction(self._create_node, key, value)

#     def delete_node(self, key):
#         with self._driver.session() as session:
#             session.write_transaction(self._delete_node, key)

#     def get_node_value(self, key):
#         with self._driver.session() as session:
#             return session.read_transaction(self._get_node_value, key)

#     @staticmethod
#     def _create_node(tx, key, value):
#         query = "CREATE (n:Node {key: $key, value: $value})"
#         tx.run(query, key=key, value=value)

#     @staticmethod
#     def _delete_node(tx, key):
#         query = "MATCH (n:Node {key: $key}) DELETE n"
#         tx.run(query, key=key)

#     @staticmethod
#     def _get_node_value(tx, key):
#         query = "MATCH (n:Node {key: $key}) RETURN n.value as value"
#         result = tx.run(query, key=key).single()
#         if result:
#             return result["value"]
#         else:
#             return None

# # Set up the connection to the Neo4j database
# neo4j_uri = "bolt://neo4j-database"
# # neo4j_uri = "bolt://localhost:7687"
# neo4j_user = "neo4j"
# neo4j_password = "password"  # Replace with your actual password

# db = Neo4jDB(neo4j_uri, neo4j_user, neo4j_password)

# # @app.route('/create_node', methods=['POST'])
# # def create_node():
# #     data = request.get_json()
# #     key = data.get('key')
# #     value = data.get('value')

# #     # Log the cache node involved in the process
# #     logger.info("Creating node for key: %s", key)

# #     # Check if the data is in the cache
# #     cached_value = cache_client.get(key)
# #     if cached_value is not None:
# #         result = cached_value
# #         logger.info("Data exists in cache for key: %s", key)
# #     else:
# #         # If not in cache, create the node and add to the cache
# #         db.create_node(key, value)
# #         result = {"message": "Node created successfully"}

# #         # Add to the cache
# #         cache_client.set(key, result, time=3600)
# #         logger.info("Data added to cache for key: %s", key)

# #     return jsonify(result)

# @app.route('/create_node', methods=['POST'])
# def create_node():
#     data = request.get_json()
#     key = data.get('key')
#     value = data.get('value')

#     # Get the cache node using consistent hashing
#     node_name = None
#     try:
#         node_name = cache_client.get(key)
#     except pylibmc.ServerDown as sd:
#         logger.error("Memcached server is down for key: %s. Error: %s", key, sd)
#         return jsonify({"message": "Memcached server is down"})

#     # Log the cache node involved in the process
#     logger.info("Creating node for key: %s on cache node: %s", key, node_name)

#     # Check if the data is in the cache
#     try:
#         cached_value = cache_client.get(key)
#     except pylibmc.ServerDown as sd:
#         logger.error("Memcached server is down when retrieving data for key: %s. Error: %s", key, sd)
#         return jsonify({"message": "Memcached server is down"})

#     if cached_value is not None:
#         result = cached_value
#         logger.info("Data exists in cache for key: %s on cache node: %s", key, node_name)
#     else:
#         # If not in cache, create the node and add to the cache
#         db.create_node(key, value)
#         result = {"message": "Node created successfully"}

#         # Add to the cache with a specific node as the key
#         try:
#             cache_client.set(key, result, time=3600)
#             logger.info("Data added to cache for key: %s on cache node: %s", key, node_name)
#         except pylibmc.ServerDown as sd:
#             logger.error("Memcached server is down when adding data to the cache for key: %s. Error: %s", key, sd)
#             return jsonify({"message": "Memcached server is down"})

#     return jsonify(result)




# @app.route('/delete_node', methods=['POST'])
# def delete_node():
#     data = request.get_json()
#     key = data.get('key')

#     # Log the cache node involved in the process
#     logger.info("Deleting node for key: %s", key)

#     if key in cache_client:
#         cache_client.delete(key)  # Remove from cache
#         db.delete_node(key)  # Delete the node in the database
#         result = {"message": "Node deleted successfully"}
#         logger.info("Node deleted from cache and database for key: %s", key)
#     else:
#         result = {"message": "Node not found in cache"}
#         logger.info("Node not found in cache for key: %s", key)

#     return jsonify(result)

# @app.route('/get_value', methods=['GET'])
# def get_value():
#     data = request.get_json()
#     key = data.get('key')

#     # Log the cache node involved in the process
#     logger.info("Getting value for key: %s", key)

#     cached_value = cache_client.get(key)
#     if cached_value is not None:
#         result = cached_value
#         logger.info("Data retrieved from cache for key: %s", key)
#     else:
#         value = db.get_node_value(key)
#         if value is not None:
#             result = value
#             cache_client.set(key, value, time=3600)
#             logger.info("Data retrieved from database and added to cache for key: %s", key)
#         else:
#             result = {"message": "Node not found with the given key"}
#             logger.info("Node not found in cache and database for key: %s", key)

#     return jsonify(result)

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=4000, debug=True)

from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache (you might want to use a more sophisticated solution for production)
cache = {}

@app.route('/create_node', methods=['POST'])
def create_node():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')

    if key is None or value is None:
        logger.error('Both key and value are required.')
        return jsonify({'error': 'Both key and value are required'}), 400

    if key in cache:
        logger.warning(f'Node with key {key} already exists. Reusing existing value.')
    else:
        logger.info(f'Creating node with key {key} and value {value}.')
        cache[key] = value

    return jsonify({'message': f'Node with key {key} created or updated successfully'})

@app.route('/delete_node', methods=['POST'])
def delete_node():
    data = request.get_json()
    key = data.get('key')

    if key is None:
        logger.error('Key is required.')
        return jsonify({'error': 'Key is required'}), 400

    if key in cache:
        del cache[key]
        logger.info(f'Node with key {key} deleted successfully.')
        return jsonify({'message': f'Node with key {key} deleted successfully'})
    else:
        logger.warning(f'Node with key {key} not found.')
        return jsonify({'error': f'Node with key {key} not found'}), 404

@app.route('/get_value', methods=['GET'])
def get_value():
    data = request.get_json()
    key = data.get('key')

    if key is None:
        logger.error('Key parameter is required.')
        return jsonify({'error': 'Key parameter is required'}), 400

    value = cache.get(key)
    if value is not None:
        logger.info(f'Retrieved value for key {key}.')
        return jsonify({'key': key, 'value': value})
    else:
        logger.warning(f'Node with key {key} not found.')
        return jsonify({'error': f'Node with key {key} not found'}), 404

# Endpoint to retrieve all key-value pairs in the cache
@app.route('/get_all_data', methods=['GET'])
def get_all_data():
    return jsonify(cache)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)

