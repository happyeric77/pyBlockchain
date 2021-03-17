import transaction as tx
import blockchain
from flask import Flask, jsonify, request
import pickle, sys, json, requests
import threading

app = Flask(__name__)
host = "0.0.0.0"

if len(sys.argv) < 2:
    print("please defind port by --port")
else:
    if sys.argv[1].startswith("--"):
        option = sys.argv[1][2:]
        if option == "port":
            port = int(sys.argv[2])
    else:
        print("please defind port by --port")

chain = blockchain.Blockchain(host, port)

@app.route("/mine_block/<name>/<amount>", methods = ["GET"])
def mindCoinBaseBlock(name, amount, chain=chain):
    chain.syncNode(host, port)
    coin = tx.Transaction("coinbase", {name: int(amount)})

    byteCoin = pickle.dumps(coin)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteCoin, chain.getLastID_Hash()[1])
    newBlock.mineBlock()
    chain.addBlock(newBlock)
    chain.syncNode(host, port)
    
    response = {
        "sender": name,
        "amount": amount,
        "newBlock": {
            "id": newBlock.index,
            "hash": newBlock.hash,
            "previous hash": newBlock.prevHash
        }
    }
    jsonify(response)
    return jsonify(response)

@app.route("/transfer/", methods = ["POST"])
def mindTransactionBlock():
    chain.syncNode(host, port)
    req = request.get_json()
    sender = req["sender"]
    to = req["to"]
    amount = req["amount"]
    trx = tx.Transaction(sender, {to: int(amount)})
    balance = trx.updateInputs(chain)    
    
    byteTx = pickle.dumps(trx)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteTx, chain.getLastID_Hash()[1])
    
    newBlock.mineBlock()
    chain.addBlock(newBlock)
    chain.syncNode(host, port)
    response = {
        "sender": sender,
        "amount": amount,
        "newBlock": {
            "id": newBlock.index,
            "hash": newBlock.hash,
            "previous hash": newBlock.prevHash
        },
        "transaction": {
            "balance": balance,
            "txid": trx.id
        }
    }
    return jsonify(req)

@app.route("/printBlocks/", methods = ["GET"])
def printBlocks(chain=chain):
    blocksData = chain.printBlocks()
    return jsonify(blocksData)


#TODO 
@app.route("/get_nodes/", methods = ["GET"])
def get_nodes():
    nodes = [node for node in chain.nodes]
    return jsonify(nodes)

@app.route("/get_chain/", methods = ["GET"])
def get_chain():
    return pickle.dumps(chain)

@app.route("/sync_nodes/", methods = ["GET"])
def sync_nodes():
    chain.syncNode(host, port)
    return jsonify([node for node in chain.nodes])

# @app.route("/add_nodes/<node>", methods = ["GET"])
# def add_nodes(node):
#     # def outputNode():
#     nodesToAdd = requests.get(f"http://{node}/output_nodes").json()
#     chain.nodes.update(nodesToAdd)
#     # outputNodeThread = threading.Thread(target=outputNode)
#     # outputNodeThread.start()
#     return jsonify(nodesToAdd)

# @app.route("/output_nodes/", methods = ["GET"])
# def output_nodes():
#     # chain.nodes
#     return jsonify([node for node in chain.nodes])



if __name__ == "__main__":        

    # To fix the issue "AttributeError: 'Request' object has no attribute 'is_xhr'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    """
    The request.is_xhr property was deprecated since Werkzeug 0.13 and removed in Werkzeug 1.0.0. 
    You will get this error when using Flask <= 0.12.4 and Werkzeug >=1.0.0 because Flask uses this property in the source before the 1.0.0 version. 
    You can just upgrade Flask (>=1.0.0) to fix this issue
    """ 

    # Run Flask 

    app.run(host=host, port=port)
    """
    Equivalant as doing following step on cli
    1. export FLASK_APP=main.py (Add FLASK_APP into env variable)
    2. python -m flask run --host 0.0.0.0 (Flask default port is 5000)
    """
    






        

