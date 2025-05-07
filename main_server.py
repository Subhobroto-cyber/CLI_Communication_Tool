from flask import Flask, request, jsonify
import uuid
import hashlib

app = Flask(__name__)

# Temporary in-memory storage
temp_storage = {
    "servers": []
}

def hash_key(raw_key):
    return hashlib.sha256(raw_key.encode()).hexdigest()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    ip = request.remote_addr
    port = data.get('port')
    is_public = data.get('public', False)

    if not port:
        return jsonify({"error": "Port is required"}), 400

    # Prevent duplicate registration
    for server in temp_storage["servers"]:
        if server["ip"] == ip and server["port"] == port:
            return jsonify({"error": "Server already registered"}), 409

    if is_public:
        # Public server registration
        server = {"ip": ip, "port": port, "key": None, "public": True}
        temp_storage["servers"].append(server)
        return jsonify({"message": "Public server registered", "ip": ip, "port": port}), 201
    else:
        # Private server registration with hashed key
        raw_key = str(uuid.uuid4())
        hashed = hash_key(raw_key)
        server = {"ip": ip, "port": port, "key": hashed, "public": False}
        temp_storage["servers"].append(server)
        return jsonify({
            "message": "Private server registered",
            "key": raw_key,  # return unhashed version for user to use
            "ip": ip,
            "port": port
        }), 201

@app.route('/lookup', methods=['GET'])
def lookup():
    raw_key = request.args.get('key')
    if not raw_key:
        return jsonify({"error": "Key is required"}), 400

    hashed = hash_key(raw_key)
    for server in temp_storage["servers"]:
        if server.get("key") == hashed:
            return jsonify({"ip": server['ip'], "port": server['port']}), 200

    return jsonify({"error": "Server not found"}), 404

@app.route('/public_servers', methods=['GET'])
def public_servers():
    public_list = [server for server in temp_storage["servers"] if server.get("public")]
    return jsonify(public_list), 200

@app.route('/remove', methods=['POST'])
def remove_server():
    data = request.json
    ip = request.remote_addr
    port = data.get('port')

    if not port:
        return jsonify({"error": "Port is required"}), 400

    before_count = len(temp_storage["servers"])
    temp_storage["servers"] = [
        server for server in temp_storage["servers"]
        if not (server["ip"] == ip and server["port"] == port)
    ]
    after_count = len(temp_storage["servers"])

    if before_count == after_count:
        return jsonify({"message": "No matching server found"}), 404

    return jsonify({"message": "Server removed"}), 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "OK", "registered_servers": len(temp_storage["servers"])}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
