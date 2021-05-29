from flask import Flask, jsonify, request
from blockchain import Blockchain
import time
from uuid import uuid4
import re

# Creating a web app
app = Flask(__name__)

# set the port #
PORT = 5002

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Create a Blockchain
blockchain = Blockchain()

@app.route("/mine_block", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_latest_block()
    previous_proof = previous_block.proof
    start = time.time()
    proof = blockchain.proof_of_work(previous_proof)
    end = time.time() - start
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver=f"User {PORT}", amount=1, memo="Block Reward.")
    block = blockchain.create_block(proof, previous_hash, end)
    response = {
        "message": "Congratulations, you just mined a block!",
        "work_time": end,
        "index": block.index,
        "timestamp": block.timestamp,
        "proof": block.proof,
        "previous_hash": block.previous_block_hash,
        "transactions": block.transaction_list,

    }
    return jsonify(response), 200

@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain)
    }
    return str(response), 200

@app.route("/is_valid", methods=["GET"])
def is_valid():
    if blockchain.is_chain_valid(blockchain.chain):
        response = {"message": "The Blockchain is valid."}
    else:
        response = {"message": "The blockchain is not valid."}
    return jsonify(response), 200

@app.route("/avg_mine_time", methods=["GET"])
def avg_mine_time():
    stop = 4
    response = {}
    base = multiplier = previous = 1
    total = short_total = 0
    for block in blockchain.chain:
        total += block.time_to_mine
        short_total += block.time_to_mine
        if block.index == (base * 10**multiplier):
            response[f"{previous}-{block.index} Average"] = short_total / (block.index - previous)
            short_total = 0
            previous = block.index
            if base == stop:
                base = 0
                multiplier += 1
            base += 1
    response["Total Average"] = total / len(blockchain.chain)

    return jsonify(response), 200


@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    js = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
    if not all (key in js for key in transaction_keys):
        return "some elements of the transaction are missing", 400
    index = blockchain.add_transaction(*(js[t] for t in transaction_keys))
    response = {"message": f"This transaction will be added to Block {index}"}
    return jsonify(response), 201


@app.route("/connect_node", methods=["POST"])
def connect_node():
    js = request.get_json()
    nodes = js.get("nodes")
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {
        "message": "All the nodes are now connected. This blockchain now contains the following nodes:",
        "total_nodes": list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route("/replace_chain", methods=["POST"])
def replace_chain():
    needs_replacing = blockchain.replace_chain()
    if needs_replacing:
        response = {
            "message": "The node had different chains so it was replaced by the largest one.",
            "new_chain": [repr(chain) for chain in blockchain.chain]
        }
    else:
        response = {
            "message": "All good. The chain is the largest one.",
            "actual_chain": [repr(chain) for chain in blockchain.chain]
        }
    return jsonify(response), 200


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.run(host="0.0.0.0", port=PORT)

