import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
import json
import copy
import random
import secrets
import docker

client = docker.from_env()


def get_source():
	for container in client.containers.list():
		if container.name == 'lnd_testnet_source':
			return container
	raise Exception("source not running")


def get_target():
	for container in client.containers.list():
		if container.name == 'lnd_testnet':
			return container
	raise Exception("target not running")



def find_min_balance(source, target, path):
	high = 2**24 - 1
	low = 0
	while low < high:
		print(low, high)
		amt = (low + high)//2
		
		#get a random hash
		payment_hash = secrets.token_hex(32)
		# print(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))
		res = source.exec_run(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))
		print(res)
		assert get_attr(res, 'payment_error') != ""
		assert get_attr(res, 'payment_preimage') == ""
		if msg_reached(target, payment_hash):
			low = amt + 1
		else:
			high = amt

	print(low, high)
	print("The maximum balance which can be sent via bob-carol channel is " + str(low - 1 ))
	return

def msg_reached(node, hash):
	log = node.logs().decode('utf-8')
	return (hash in log)


def main():
	source = get_source()
	target = get_target()
	path = json.loads('{"routes":[{"total_time_lock":1513572,"total_fees":"3","total_amt":"1004","hops":[{"chan_id":"1662850808316231681","chan_capacity":"16777215","amt_to_forward":"1002","fee":"2","expiry":1513428,"amt_to_forward_msat":"1002001","fee_msat":"2001","pub_key":"03a13a469bae4785e27fae24e7664e648cfdb976b97f95c694dea5e55e7d302846"},{"chan_id":"1491206048232308736","chan_capacity":"16777215","amt_to_forward":"1001","fee":"1","expiry":1513388,"amt_to_forward_msat":"1001000","fee_msat":"1001","pub_key":"0270685ca81a8e4d4d01beec5781f4cc924684072ae52c507f8ebe9daf0caaab7b"},{"chan_id":"1637259675180990464","chan_capacity":"16000000","amt_to_forward":"1001","fee":"0","expiry":1513388,"amt_to_forward_msat":"1001000","fee_msat":"0","pub_key":"030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673"}],"total_fees_msat":"3002","total_amt_msat":"1004002"}]}')
	find_min_balance(source, target, path)

"""
'{
	"routes": [
		{
			"total_fees": "1",
			"total_amt": "2",
			"hops": [
				{
					"chan_id": "359540302348288",
					"chan_capacity": "100000",
					"amt_to_forward": "1",
					"fee": "1",
					"expiry": 381,
					"amt_to_forward_msat": "1000",
					"fee_msat": "1000",
					"pub_key": "02d35cb4e7552382ba77f359e0590dad101c05ac746a0ab8bb6ada12b730bacf15"
				},
				{
					"chan_id": "359540302479360",
					"chan_capacity": "100000",
					"amt_to_forward": "1",
					"fee": "0",
					"expiry": 381,
					"amt_to_forward_msat": "1000",
					"fee_msat": "0",
					"pub_key": "02f8c14bdf90d49dae88c4573f7d70bfb2c4d3bc25401894fb08f4cfc565924d8b"
				},
				{
					"chan_id": "359540302413824",
					"chan_capacity": "100000",
					"amt_to_forward": "1",
					"fee": "0",
					"expiry": 381,
					"amt_to_forward_msat": "1000",
					"fee_msat": "0",
					"pub_key": "0217531a8acb54b2fad4215f318f82dea72976fbb7d8a600806bea5b97c8e5f84a"
				}
			],
			"total_fees_msat": "1000",
			"total_amt_msat": "2000"
		}
	]
}'
"""

# def main():
# 	num_nodes = 4
# 	network = networkinitializer.setup(num_nodes, with_balance = True)

# 	bitcoind = network.bitcoind_node
# 	lnd_nodes = network.lnd_nodes

# 	alice = lnd_nodes[0]
# 	bob = lnd_nodes[1]
# 	carol = lnd_nodes[2]
# 	dave = lnd_nodes[3]




# 	# Open connection from Alice to Bob and Bob to Carol and Coral to Alice
# 	capacity = 2**21-1
# 	res = alice.container.exec_run(createconnection(bob))
# 	res = alice.container.exec_run(openchannel(bob, capacity))

# 	res = bob.container.exec_run(createconnection(carol))
# 	res = bob.container.exec_run(openchannel(carol, capacity))

# 	res = carol.container.exec_run(createconnection(dave))
# 	res = carol.container.exec_run(openchannel(dave, capacity))


# 	# confirm the funding transactions; only 3 are needed for lnd
# 	bitcoind.container.exec_run(generatetoaddress(6))

# 	time.sleep(2)
# 	# THis is wait time for network so that all payments are along the same route
# 	time.sleep(15)

# 	# We do not control a bob-carol link. The attacker can only control nodes alice and dave
	
# 	# Step 1: send a random amount from bob to carol and try to infer that amount from out algorithm
# 	invoice_amt = random.randint(0,(capacity*99)//100)
# 	res = carol.container.exec_run(getinvoice(invoice_amt))
# 	pay_req = get_attr(res, 'pay_req')

# 	print(str(invoice_amt) + " is the final invoice_amt ")


# 	res = bob.container.exec_run(sendpayment(pay_req))
# 	# print(res.output.decode('utf-8'))

# 	# Step 2: Payment inference using binary search
# 	invoice_amt = 100
# 	res = dave.container.exec_run(getinvoice(invoice_amt))
# 	pay_req = get_attr(res, 'pay_req')
# 	payment_hash = get_attr(res, 'r_hash')
# 	# print(payment_hash)

# 	# We need to parse the structure of the queryroutes 
# 	res = alice.container.exec_run(queryroutes(dave, invoice_amt))
# 	routes = json.loads(res.output.decode('utf-8'))

# 	# find_last_hop(); add last hop to routes
# 	# print(routes)
# 	#Change this later
# 	exec_res = alice.container.exec_run(getinfo())
# 	height = int(json.loads(exec_res.output.decode('utf-8')).get('block_height'))

if __name__ == "__main__":
	main()
