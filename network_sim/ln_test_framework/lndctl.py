# controller for bitcoind
def regtest_context():
	context = {}
	context['cmd'] = "./lncli --network=regtest --no-macaroons "
	return context

def testnet_source_context():
	context = {}
	context['cmd'] = "./lncli --no-macaroons --network=testnet --rpcserver=localhost:10011"
	return context

def get_context(chain):
	if chain == 'regtest':
		return regtest_context()
	if chain == 'source_testnet':
		return testnet_source_context()

def getnewaddress(chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " newaddress np2wkh" 

def getinfo(chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " getinfo"

def createconnection(node_to ,chain='regtest'):
	context = get_context(chain)
	return context['cmd'] + " connect " + node_to.pubkey + "@" + node_to.ip_address

def walletbalance(chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " walletbalance"

def openchannel(node_to, amt, chain= 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " openchannel --node_key="+node_to.pubkey +" --local_amt="+str(amt)

def getinvoice(amt, chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " addinvoice --amt="+str(amt)

def listchannels(chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " listchannels"

def sendpayment(pay_req, chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " sendpayment -f --pay_req="+pay_req

def grief(chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " grief"

def queryroutes(node_to, amt, chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " queryroutes " + node_to.pubkey + " " + str(amt)

def sendtoroute(payment_hash, routes, chain = 'regtest'):
	context = get_context(chain)
	return context['cmd'] + " sendtoroute --payment_hash=" + payment_hash + " --routes=" + routes

def describegraph(chain = 'source_testnet'):
	context = get_context(chain)
	return context['cmd'] + " describegraph"