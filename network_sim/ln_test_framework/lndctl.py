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