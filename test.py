from web3 import Web3
import json
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

abi = json.loads('[{"constant":true,"inputs":[],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"int256"}],"name":"sendEther","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"functionCalled","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
contract_address = web3.toChecksumAddress("0x60e121864013430b1526f65bC20417DD2ECb53F0")


contract = web3.eth.contract(address=contract_address, abi=abi)
account_1 = contract.functions.getOwner().call()
account_2 = "0x7599BCeb5AA26E4045B68593534CEBe66DB4A6a4"
private_key = "232c1a2b15b9be76a1778fef92862ba0a7e54babe2c08e2d08e2860cc01231e5"

nance = web3.eth.getTransactionCount(account_1)
tx = {
    'nonce': nance,
    'to': account_2,
    'value': web3.toWei(1, 'ether'),
    'gas': 2000000,
    'gasPrice': web3.toWei('50', 'gwei')
}

signed_tx = web3.eth.account.signTransaction(tx, private_key)
tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
has = web3.eth.getTransactionReceipt(tx_hash)
print(web3.toHex(tx_hash))
print(has)