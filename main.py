import transaction as tx
import blockchain
from flask import Flask, jsonify
import pickle

app = Flask(__name__)

chain = blockchain.Blockchain()

@app.route("/mine_block/<name>/<amount>", methods = ["GET"])
def mindCoinBaseBlock(name, amount, chain=chain):
    coin = tx.Transaction("coinbase", {name: int(amount)})

    byteCoin = pickle.dumps(coin)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteCoin, chain.getLastID_Hash()[1])
    newBlock.mineBlock()
    chain.addBlock(newBlock)
    
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

@app.route("/transfer/<sender>/<to>/<amount>", methods = ["GET"])
def mindTransactionBlock(sender, to, amount, chain=chain):
    trx = tx.Transaction(sender, {to: int(amount)})
    balance = trx.updateInputs(chain)    
    
    byteTx = pickle.dumps(trx)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteTx, chain.getLastID_Hash()[1])
    
    newBlock.mineBlock()
    chain.addBlock(newBlock)
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
    return jsonify(response)

@app.route("/printBlocks/", methods = ["GET"])
def printBlocks(chain=chain):
    blocksData = chain.printBlocks()
    return jsonify(blocksData)


if __name__ == "__main__":        

    # To fix the issue "AttributeError: 'Request' object has no attribute 'is_xhr'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    """
    The request.is_xhr property was deprecated since Werkzeug 0.13 and removed in Werkzeug 1.0.0. 
    You will get this error when using Flask <= 0.12.4 and Werkzeug >=1.0.0 because Flask uses this property in the source before the 1.0.0 version. 
    You can just upgrade Flask (>=1.0.0) to fix this issue
    """ 

    # Run Flask 
    app.run(host="0.0.0.0", port=5000)
    """
    Equivalant as doing following step on cli
    1. export FLASK_APP=main.py (Add FLASK_APP into env variable)
    2. python -m flask run --host 0.0.0.0 (Flask default port is 5000)
    """
    






        

