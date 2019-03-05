# controller for bitcoind
def regtest_context():
	context = {}
	context['cmd'] = "./src/bitcoin-cli -regtest "
	return context

regtest = regtest_context()

def generatetoaddress(nblocks, address="2N3oCfa8uPRCpewULR6Vut8sScx97Jn4hBj", context=regtest, ):
	return context['cmd'] + " generatetoaddress "+ str(nblocks)+ " " + address 
