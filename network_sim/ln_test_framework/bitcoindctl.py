# controller for bitcoind
def regtest_context():
	context = {}
	context['cmd'] = "./src/bitcoin-cli -regtest "
	return context

def get_context(chain):
	if chain == 'regtest':
		return regtest_context()

def generatetoaddress(nblocks, address="2N3oCfa8uPRCpewULR6Vut8sScx97Jn4hBj", chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " generatetoaddress "+ str(nblocks)+ " " + address 
