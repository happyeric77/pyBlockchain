import datetime
import hashlib
import json
from flask import Flask, jsonify
import transaction as tx
import pickle
import requests
import threading

main_nodes = set(
    [
        "0.0.0.0:5000",
        "0.0.0.0:5001",
        "0.0.0.0:5002",
    ]
)

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
    # def __init__(self):
    #TODO
    def __init__(self, host, port):        
        self.blocks = [Block(0, pickle.dumps(tx.Transaction("Genesis", {"Genesis":"Genesis"})) , 0)]
        self.txs = []
        self.UTXOs = []
        #TODO
        self.nodes = main_nodes

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
        blocksData = []
        for block in self.blocks:
            txData = pickle.loads(block.transaction)
            blockData = {
                "blockID": str(block.index),
                "prevHash": str(block.prevHash),
                "hash": str(block.hash),
                "nonce": str(block.nonce),
                "transactions": {
                    "txid": txData.id,
                    "sender": txData.sender,
                    "outs": json.dumps(txData.outs),
                    "inputs": [{"id": input.id, "out": input.out} for input in txData.inputs]
                }
            }            
            blocksData.append(blockData)
        blocksData = {
            "bestHeight":len(blocksData),
            "data": blocksData
        }
        return blocksData
        
    def is_valid(self):
        for block in self.blocks:
            if block.prevHash == self.blocks[block.index-1].hash:
                print(f"Block#{str(block.index)} is valid")

    def validateChain(self, chain) -> bool:
        for block in chain.blocks:
            if block.prevHash == self.blocks[block.index-1].hash:
                print(f"Block#{str(block.index)} is valid")
            else:
                return False
        return True


    def find_Txs(self) -> [str]:
        self.txs = []
        for block in self.blocks:
            txByte = block.transaction
            tx = pickle.loads(txByte)
            self.txs.append(tx.id)
        return self.txs

    def outputNodes(self):
        return self.nodes

    def addNodes(self, nodes):
        self.nodes.update(nodes)


    #TODO
    def syncNode(self, host: str, port: int):
        main_nodes.add(f"{host}:{port}")
        syncedNode = set()
        
        # Get the blockchain's nodes inside defined main_nodes
        # And Add it to self.nodes
        # [syncedNode.add(x) for x in main_nodes]
        syncedNode.update(main_nodes)
        syncedNode.add(f"{host}:{port}")
        for node in main_nodes:
            # if node != f"{host}:{str(port)}": 
            def syncGetNode():        
                try:
                    print(f"http://{node}/get_nodes/")
                    resNodes = requests.get(f"http://{node}/get_nodes/").json()
                    resNodesSet = set()
                    resNodesSet.update(resNodes)
                    syncedNode.update(resNodes) 
                    # if syncedNode != resNodesSet:
                    #     try:
                    #         def addNodes():
                    #             res = requests.get(f"http://{node}/add_nodes/{host}:{port}")
                                
                    #         addNodesTread = threading.Thread(target=addNodes)
                    #         addNodesTread.start()
                    #     except:
                    #         print("Get nodes fail")
                except:
                    print(f"Connection refused on {node}")
                    syncedNode.remove(node)
            syncGetNodeThread = threading.Thread(target=syncGetNode)
            syncGetNodeThread.start()
        
        self.nodes = syncedNode
        

        #TODO
        #Compare all nodes' blockchain length. if other chian's length is longer, replace with it.
        newNodes = set()
        copySelfNode = set()
        copySelfNode.update([node for node in self.nodes])
        for node in copySelfNode:
            chain = None
            if node != f"{host}:{str(port)}":
                try:
                    rawChain = requests.get(f"http://{node}/get_chain/").content
                    chain = pickle.loads(rawChain)
                    newNodes.add(node)
                except:
                    print(f"Cannot connect to {node}, removed from nodes list")

            if chain and len(chain.blocks)>len(self.blocks):
                print(self.validateChain(chain))
                if self.validateChain(chain):
                    print(f"Height of {node}'s chain({len(chain.blocks)}) >  height of {host}:{str(port)}'s chain ({len(self.blocks)}), self.chain will be replaced.")
                    self.blocks = chain.blocks
                    print("Done")
            
            elif chain and len(chain.blocks)<len(self.blocks):

                # create a sync clousure
                def askNodeToSync():
                    print(f"Height of {node}'s chain({len(chain.blocks)}) <  height of {host}:{str(port)}'s chain ({len(self.blocks)})\nAsk node to sync")
                    try:
                        res = requests.get(f"http://{node}/sync_nodes/")
                        if res.status_code == 200:
                            print("Done")
                        else:
                            print("Fail")
                    except:
                        print("Fail")
                syncRequest = threading.Thread(target=askNodeToSync)
                syncRequest.start()
                    
            self.nodes = newNodes
            self.nodes.add(f"{host}:{port}")
        

        




    

            
            

        











    






        

