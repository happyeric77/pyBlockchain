import blockchain 
import pickle
import hashlib
import json

class Input:
    def __init__(self, sender: str, id):
        self.id = id
        self.out: str = sender

class Transaction:
    def __init__(self, sender: str, outs: {str:int}) :
        self.id = None
        self.sender = sender
        self.outs = outs
        self.inputs: [Input] = []
        self.is_coinBase()
        self.hashTx() if self.is_coinBase() != True else 0

    def is_coinBase(self) -> bool:
        if self.sender == "coinbase":
            input = Input("coinbaseInId", "coinbaseOut")
            self.inputs = [input]
            self.id = "coinbaseTxId"
            return True
        return False
        
    def updateInputs(self, chain: blockchain.Blockchain):
        print(f"From {self.sender} to {self.outs}")
        
        # Find out all Transaction to sender (tx.outs[sender])
        allTxs = []
        utxos = []
        for block in chain.blocks:
            tx = pickle.loads(block.transaction)
            print(f"History outputs: \nID:  {tx.id}  ---> {tx.outs}")
            if self.sender in tx.outs.keys():
                allTxs.append(tx.id)
                utxos.append(tx)
        
        print(f"All Txs: {allTxs}")
        # delete paid tx (loop through all block tx, fillter out othose txs which are refered by inputs  )
        for block in chain.blocks:
            
            tx = pickle.loads(block.transaction)
            for input in tx.inputs:
                print(f"Tx inputs = {input.id}/ {input.out}")
                for index, txid in enumerate(allTxs):
                    if input.id == txid:
                        if self.sender in input.out:             
                            del allTxs[index]
        

        # Accumulate balance
        print(f"UTXOs {allTxs}")
        balance = 0
        for block in chain.blocks:
            tx = pickle.loads(block.transaction)

            if tx.id in allTxs:
                balance += tx.outs[self.sender]
        print(f"Balance left {balance}")
        
        # Accumulate the token to pay
        pay = 0

        for key in self.outs.keys():
            pay += self.outs[key]

        print(f"total money to pay: {pay}")
        
        # select the UTXOs going to be used
        usingUTXOs =[]
        utxoAmount = 0
        if balance > pay:
            for block in chain.blocks:
                tx = pickle.loads(block.transaction)
                if tx.id in allTxs:
                    utxoAmount += tx.outs[self.sender]
                    usingUTXOs.append(tx.id)
                    if utxoAmount > pay:
                        break
        else:
            raise EnvironmentError("You do not have enough token to pay")

        print(f"The utxos amount being used: {utxoAmount}")

        # Calculate the amount left after doing input - ouput
        leftAmount = utxoAmount

        for key in self.outs.keys():
            leftAmount -= self.outs[key]

        print(f"Amount left after paying: {leftAmount}")

        # Refund the remaining token back to self.sender:
        self.outs[self.sender] = leftAmount


        # Add txs going to pay into self.inputs
        for txid in usingUTXOs:            
            self.inputs.append(Input(self.sender, txid))
        
        print(f"Outpus of this tx: {self.outs}")
        print("*"*100)

    def hashTx(self):
        byteTx = pickle.dumps(self)
        self.id = hashlib.sha256(byteTx).hexdigest()

