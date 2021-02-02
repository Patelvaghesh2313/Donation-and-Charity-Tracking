import json
from web3 import Web3
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

abi = json.loads('[{"constant":true,"inputs":[],"name":"getBalance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"amt","type":"int256"}],"name":"sendEther","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"functionCalled","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]')
contract_address = web3.toChecksumAddress("0x60e121864013430b1526f65bC20417DD2ECb53F0")


contract = web3.eth.contract(address=contract_address, abi=abi)
balance = contract.functions.getBalance().call()
owner = contract.functions.getOwner().call()
receiver = '0x7599BCeb5AA26E4045B68593534CEBe66DB4A6a4'
sender = '0x7599BCeb5AA26E4045B68593534CEBe66DB4A6a4'
#web3.eth.sendTransaction({from:sender,to:receiver,value:1})
print(owner)
print(web3.fromWei(balance,'ether'))
print("Vaghesh")


