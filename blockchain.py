import datetime
import hashlib
import json
import math
from urllib.parse import urlparse

import requests


class Block:
    def __init__(self, index, previous_block_hash, transaction_list, proof, time_to_mine=0):
        self.index = index
        self.timestamp = datetime.datetime.utcnow()
        self.proof = proof
        self.previous_block_hash = previous_block_hash
        self.transaction_list = transaction_list
        self.time_to_mine = time_to_mine

    def __repr__(self):
        return json.dumps({
            "index": self.index,
            "timestamp": str(self.timestamp),
            "proof": self.proof,
            "previous_hash": self.previous_block_hash,
            "transactions": self.transaction_list,
            "work_time": self.time_to_mine
        })


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash="START")
        self.nodes = set()

    def create_block(self, proof, previous_hash, time_to_mine=0):
        block = Block(len(self.chain) + 1, previous_hash, self.transactions, proof, time_to_mine)
        self.transactions = []
        self.chain.append(block)
        return block

    def get_latest_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        nonce_count = math.floor(math.log10(len(self.chain))) + 4
        while True:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:nonce_count] == "0" * nonce_count:
                return new_proof
            new_proof += 1

    def hash(self, block):
        return hashlib.sha256(repr(block).encode()).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            nonce_count = math.floor(math.log10(block_index)) + 4
            if block.previous_block_hash != self.hash(previous_block):
                return False
            hash_operation = hashlib.sha256(str(block.proof**2 - previous_block.proof**2).encode()).hexdigest()
            if hash_operation[:4] != "0000":
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        previous_block = self.get_latest_block()
        return previous_block.index + 1

    def add_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)


    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"https://{node}/get_chain")
            if response.status_code == 200:
                # TODO make sure this works without replacing quotes
                length = response.json()["length"]
                chain = json.loads(response.json()["chain"])
                chain = [Block(block["index"], block["previous_hash"], block["transactions"], block["proof"], block["work_time"]) for block in chain]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain is not None:
            self.chain = longest_chain
            return True
        return False



