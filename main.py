import transaction as tx
import blockchain
from flask import Flask
import pickle



def mindCoinBaseBlock(output, chain):
    coin = tx.Transaction("coinbase", output)


    byteCoin = pickle.dumps(coin)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteCoin, chain.getLastID_Hash()[1])
    newBlock.mineBlock()
    chain.addBlock(newBlock)



def mindTransactionBlock(sender, output, chain):
    trx = tx.Transaction(sender, output)
    trx.updateInputs(chain)    
    
    byteTx = pickle.dumps(trx)    
    newBlock = blockchain.Block(chain.getLastID_Hash()[0]+1 ,byteTx, chain.getLastID_Hash()[1])
    
    newBlock.mineBlock()
    chain.addBlock(newBlock)

if __name__ == "__main__":

    chain = blockchain.Blockchain()
    mindCoinBaseBlock({"Eric": 60}, chain)
    mindTransactionBlock("Eric", {"Yuko": 30}, chain)
    mindTransactionBlock("Eric", {"Yuko": 20}, chain)
    mindTransactionBlock("Eric", {"Yuko": 5}, chain)
    mindTransactionBlock("Yuko", {"Eric": 25}, chain)
    mindTransactionBlock("Yuko", {"Eric": 10}, chain)
    mindCoinBaseBlock({"Yuko": 20}, chain)
    mindTransactionBlock("Yuko", {"Eric": 10}, chain)

    # chain.printBlocks()
    # chain.is_valid()
    
    # chain.findUTXOs()




    






        

