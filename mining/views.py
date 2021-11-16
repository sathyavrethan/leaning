from uuid import uuid4
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import handrill.handrill
import json
import requests
from django.http import JsonResponse

node_address = str(uuid4()).replace('-','')
chainobject = handrill.handrill.blockChain()
# Create your views here.


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def minerapi(request):

    previous_block = chainobject.get_previousblock()
    previous_proof = previous_block['proof']
    proof = chainobject.proof_of_work(previous_proof)
    previous_hash = chainobject.hash(previous_block)
    chainobject.add_transactions(sender= node_address , receiver = 'test' , amount = 10)
    block = chainobject.create_block(proof, previous_hash)
    print(block)
    # Response = {'Message': block
    #             }
    Response = {'Message': 'Congragulations , you just mined a block',
                 'Index': block['index'],
                 'Timestamp': block['timestamp'],
                 'proof': block['proof'],
                'PreviousHash': block['previous_hash']
                 }
    return JsonResponse(Response, status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def getchain(request):

    Response = {'Chain': chainobject.chain,
                'Chain length': len(chainobject.chain)}
    return JsonResponse(Response, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def addtransactions(request):
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all ( key in json for key in transaction_keys):
        return 'Some keys are missing from the transaction' , 400
    index = chainobject.add_transactions(json['sender'],json['receiver'],json['amount'])
    response = {'message': f' this transaction will be added to the Block {index}'}
    return JsonResponse(response) , 201
    
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def connect_node(request):
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes found' , 400
    for node in nodes:
        chainobject.add_node(node)
    response = {'message' : 'all nodes are now connected' ,
                'total nodes': list(chainobject.nodes)
               }
    return JsonResponse(response) , 201

@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def replace_chain(request):
    is_chain_replaced = chainobject.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The chain has been replaced with the longest one due to difference in node chains',
                    'new chain': chainobject.chain
                   }
    else:
        response = {'message': 'The chain is still valid and not replaced',
                    'new chain': chainobject.chain
                   }
    return JsonResponse(response) , 200
