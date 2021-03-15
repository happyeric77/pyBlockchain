import transaction as tx
import blockchain
from flask import Flask, jsonify
import pickle
import json

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
    return json.dumps(response)

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
    return json.dumps(response)
    






        

