# from flask import Flask, request, jsonify
# import hashlib
# import requests
# import json

# app = Flask(__name__)

# # List of cache services with their names and ports
# cache_services = [
#     {"name": "cache_service", "port": 4000},
#     {"name": "cache_service2", "port": 4001},
#     {"name": "cache_service3", "port": 4002},
# ]

# def get_cache_service(key):
#     hashed_key = int(hashlib.sha1(key.encode()).hexdigest(), 16)
#     selected_service = hashed_key % len(cache_services)
#     return cache_services[selected_service]['name']

# @app.route('/forward_request', methods=['POST'])
# def forward_request():
#     data = request.get_json()
#     key = data.get('key')
#     value = data.get('value')

#     if key is None or value is None:
#         return jsonify({'error': 'Both key and value are required'}), 400

#     cache_service_name = get_cache_service(key)
#     cache_url = f"http://{cache_service_name}:{cache_services[0]['port']}/create_node"

#     try:
#         response = requests.post(cache_url, json={'key': key, 'value': value})
#         response.raise_for_status()
#         return jsonify({'message': f'Request forwarded to cache service {cache_service_name} successfully'})
#     except requests.exceptions.RequestException as e:
#         return jsonify({'error': f'Failed to forward request to cache service {cache_service_name}: {str(e)}'}), 500

# @app.route('/add_node', methods=['POST'])
# def add_node():
#     data = request.get_json()
#     name = data.get('name')
#     port = data.get('port')

#     if name is None or port is None:
#         return jsonify({'error': 'Both name and port are required for adding a node'}), 400

#     cache_services.append({"name": name, "port": port})
#     return jsonify({'message': f'Node {name} added successfully'})

# @app.route('/remove_node', methods=['POST'])
# def remove_node():
#     data = request.get_json()
#     name = data.get('name')

#     if name is None:
#         return jsonify({'error': 'Node name is required for removal'}), 400

#     cache_services[:] = [node for node in cache_services if node['name'] != name]
#     return jsonify({'message': f'Node {name} removed successfully'})

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=9000, debug=True)


from flask import Flask, request, jsonify
import hashlib
import requests
import json
import logging
import os

app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of cache services with their names and ports
# cache_services = [
#     {"name": "cache_service1", "port": 4000},
#     {"name": "cache_service2", "port": 4001},
#     {"name": "cache_service3", "port": 4002},
# ]

# Function to dynamically generate cache_services list
def generate_cache_services():
    service_count = int(os.getenv('SERVICE_COUNT'))
    return [
        {
            "name": os.getenv(f'SERVICE_NAME_{i}'),
            "port": int(os.getenv(f'SERVICE_PORT_{i}'))
        }
        for i in range(1, service_count + 1)
    ]

# List of cache services with their names and ports
cache_services = generate_cache_services()


# Hash ring structure
hash_ring = {}

# In-memory cache for key-value pairs
cache_data = {}

# Function to hash a key and determine the cache service responsible for it
def get_cache_service(key):
    hashed_key = int(hashlib.sha1(key.encode()).hexdigest(), 16)
    ring_keys = sorted(hash_ring.keys())
    for ring_key in ring_keys:
        if hashed_key <= ring_key:
            return hash_ring[ring_key]

    # If the hashed_key is greater than all ring keys, use the first node
    return hash_ring[ring_keys[0]]

# Function to update the hash ring when cache services change
def update_hash_ring():
    global hash_ring
    hash_ring = {}
    for service in cache_services:
        hash_ring[hash_key(service["name"])] = service["name"]

# Function to hash a cache service name
def hash_key(key):
    return int(hashlib.sha1(key.encode()).hexdigest(), 16)

# Function to migrate data when removing a cache service
def migrate_data(source, destination):
    global cache_data
    keys_to_migrate = [key for key in cache_data if get_cache_service(key) == source]
    
    for key in keys_to_migrate:
        value = cache_data[key]
        
        # Forward the data to the destination cache service
        migrate_url = f"http://{destination}:{cache_services[0]['port']}/create_node"
        try:
            migrate_response = requests.post(migrate_url, json={'key': key, 'value': value})
            migrate_response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
            logger.info(f"Key {key} migrated from {source} to {destination}")
        except requests.exceptions.RequestException as e:
            # Handle the case where the migration fails for a specific key
            logger.error(f"Failed to migrate key {key} from {source} to {destination}: {str(e)}")

        # Remove the data from the local cache
        del cache_data[key]

# Endpoint to add a cache service dynamically
@app.route('/add_node', methods=['POST'])
def add_node():
    data = request.get_json()
    name = data.get('name')
    port = data.get('port')

    if name is None or port is None:
        return jsonify({'error': 'Both name and port are required'}), 400

    global cache_services
    cache_services.append({"name": name, "port": port})
    update_hash_ring()

    logger.info(f'Cache service {name} added successfully')
    return jsonify({'message': f'Cache service {name} added successfully'})

# Endpoint to remove a cache service dynamically
@app.route('/remove_node', methods=['POST'])
def remove_node():
    data = request.get_json()
    node_name = data.get('node_name')

    if node_name is None:
        return jsonify({'error': 'Node name is required'}), 400

    if node_name not in [service['name'] for service in cache_services]:
        return jsonify({'error': f'Node {node_name} not found'}), 404

    # Find the index of the node to be removed
    node_index = next((i for i, service in enumerate(cache_services) if service['name'] == node_name), None)

    if node_index is not None:
        # Get the name of the next node in the hash ring
        next_node_name = cache_services[(node_index + 1) % len(cache_services)]['name']

        # Get all data from the cache service to be removed
        cache_url = f"http://{node_name}:{cache_services[0]['port']}/get_all_data"
        try:
            response = requests.get(cache_url)
            response.raise_for_status()
            data_to_migrate = response.json()

            # Migrate data from the removed node to the next node
            for key, value in data_to_migrate.items():
                migrate_url = f"http://{next_node_name}:{cache_services[0]['port']}/create_node"
                try:
                    migrate_response = requests.post(migrate_url, json={'key': key, 'value': value})
                    migrate_response.raise_for_status()
                    logger.info(f"Key {key} migrated from {node_name} to {next_node_name}")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to migrate key {key} from {node_name} to {next_node_name}: {str(e)}")

        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Failed to retrieve data from node {node_name}: {str(e)}'}), 500

        # Remove the node from the cache_services list
        del cache_services[node_index]
        update_hash_ring()

        logger.info(f'Node {node_name} removed successfully')
        return jsonify({'message': f'Node {node_name} removed successfully'})
    else:
        return jsonify({'error': f'Node {node_name} not found'}), 404

# Endpoint to forward a request based on the hash ring
@app.route('/forward_request', methods=['POST'])
def forward_request():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')

    if key is None or value is None:
        return jsonify({'error': 'Both key and value are required'}), 400

    cache_service_name = get_cache_service(key)

    # Forward the request to the appropriate cache service
    cache_url = f"http://{cache_service_name}:{cache_services[0]['port']}/create_node"  # Assuming the first cache service port is used for all

    try:
        response = requests.post(cache_url, json={'key': key, 'value': value})
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

        logger.info(f'Request forwarded to cache service {cache_service_name} successfully')
        return jsonify({'message': f'Request forwarded to cache service {cache_service_name} successfully'})
    except requests.exceptions.RequestException as e:
        logger.error(f'Failed to forward request to cache service {cache_service_name}: {str(e)}')
        return jsonify({'error': f'Failed to forward request to cache service {cache_service_name}: {str(e)}'}), 500

if __name__ == '__main__':
    update_hash_ring()
    app.run(host="0.0.0.0", port=9000, debug=True)

