# controller for bitcoind
def regtest_context():
	context = {}
	context['cmd'] = "./lncli --network=regtest --no-macaroons "
	return context

def get_context(chain):
	if chain == 'regtest':
		return regtest_context()

def getnewaddress(chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " newaddress np2wkh" 

def getinfo(chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " getinfo"

def createconnection(node_to ,chain='regtest')
	context = get_context(chain)
	return context['cmd'] + " connect " + node_to.pubkey + "@" + node_to.ip_address