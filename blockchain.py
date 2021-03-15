import datetime
import hashlib
import json
from flask import Flask, jsonify
import transaction as tx
import pickle


class Block:
    def __init__(self, id: int, transaction: bytes, prevHash: int):
        self.index = id
        self.difficulty = 12
        self.nonce = 0
        self.transaction = transaction
        self.timestamp = int(datetime.datetime.now().timestamp())
        self.target = 0
        self.prevHash = prevHash
        self.hash = 0
        self.calcTarget()

    def encodeData(self) -> bytes:
        data = {
            "index": str(self.index),
            "difficulty": str(self.difficulty),
            "nonce": str(self.nonce),
            "transaction": str(self.transaction),
            "timestamp": str(self.timestamp),
            "prevHash": str(self.prevHash)
        }
        byteData = json.dumps(data, sort_keys=True).encode()
        return byteData
    
    def hashData(self, byteData: bytes) -> int:
        hexString = "0x" + hashlib.sha256(byteData).hexdigest()
        hexInt = int(hexString, 16)
        return hexInt

    def calcTarget(self) -> int:
        byteData = self.encodeData()
        hexInt = self.hashData(byteData)
        self.target = hex(hexInt >> self.difficulty)
        self.target = int(self.target, 16)
        return self.target

    def mineBlock(self):
        byteData = self.encodeData()
        hashDec = self.hashData(byteData)
        while hashDec > self.target:
            self.nonce += 1
            self.timestamp = int(datetime.datetime.now().timestamp())
            byteData = self.encodeData()
            hashDec = self.hashData(byteData)

        self.hash = hashDec

class Blockchain:
    def __init__(self):        
        self.blocks = [Block(0, pickle.dumps(tx.Transaction("Genesis", {"Genesis":"Genesis"})) , 0)]
        self.txs = []
        self.UTXOs = []

    def addBlock (self, block: Block):
        prevHash = self.blocks[-1].hash
        if prevHash != block.prevHash:
            raise RuntimeError("Block's previous hash does not match")
        else:
            if block.hash > block.target:
                raise EnvironmentError("Fail to pass POW validation")
        self.blocks.append(block)

    def getLastID_Hash(self) -> (int, int):
        return self.blocks[-1].index, self.blocks[-1].hash

    def printBlocks(self):
        print("Total block count: "+ str(len(self.blocks)))
        for block in self.blocks:
            print("block ID: " + str(block.index))
            print("Previous Hash: " + str(block.prevHash))
            print("Hash: " + str(block.hash))
            print("Nonce: " + str(block.nonce))
            print("Transactions: " + str(block.transaction))
            print("="*50)
        
    def is_valid(self):
        for block in self.blocks:
            if block.prevHash == self.blocks[block.index-1].hash:
                print(f"Block#{str(block.index)} is valid")

    def find_Txs(self) -> [str]:
        self.txs = []
        for block in self.blocks:
            txByte = block.transaction
            tx = pickle.loads(txByte)
            self.txs.append(tx.id)
        return self.txs










    






        

