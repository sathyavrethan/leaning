from typing import NewType
from django.http import response
from django.shortcuts import render

# Create your views here.
import datetime
import hashlib
import json
import requests
from uuid import uuid4
from urllib.parse import DefragResult, urlparse
import mining.views

class blockChain:
    def __init__(self):
        self.chain=[]
        self.transactions = []
        self.create_block(proof = 1 , previous_hash= '0')
        self.nodes = set()

    
    def create_block(self, proof, previous_hash):
        block={'index': len(self.chain) + 1,
               'timestamp': str(datetime.datetime.now()),
               'proof' : proof,
               'transactions' : self.transactions,
               'previous_hash ' : previous_hash }
        self.transactions = []
        self.chain.append(block)
        return block
    def get_previousblock(self):
        return self.chain[-1]
    
    def proof_of_work(self , previous_proof ):
        new_proof = 1
        check_proof = False
        hash_operation = hashlib.sha3_384(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
        if hash_operation[:4] == '0000':
            check_proof = True
        else:
            new_proof += 1
            check_proof = False
        return new_proof    
    def hash(self,block) :
        encoded_block = json.dumps(block,sort_keys=True).encode()
        return hashlib.sha3_384(encoded_block).hexdigest()

    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha3_384(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_transactions(self,sender,receiver,amount):
        self.transactions.append({'sender': sender , 
                                  'receiver': receiver, 
                                  'amount': amount})
        previous_block = self.get_previousblock()
        return previous_block['index'] + 1

    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        get_chain = mining.views.getchain
        for node in network:
            response = requests.get(f'http://{node}/mine/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True




