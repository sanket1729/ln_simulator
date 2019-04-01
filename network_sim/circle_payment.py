import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
import json
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
def make_hop(pub_key, chan_id, total_amt):
	hop = {}
	hop['pub_key'] = pub_key
	hop['chan_id'] = chan_id
	hop['amt_to_forward'] = str(total_amt)
	hop['expiry'] = 400
	hop['amt_to_forward_msat'] = str(total_amt*1000)
	hop['fee'] = 0
	hop['fee_msat'] = 0
	return hop

def create_all_but_one_edge_circle_route(routes, total_amt):
	del routes['routes'][0]['total_time_lock']
	#Pay the fees per route
	i = 0
	for hop in routes['routes'][0]['hops']:
		i = i + 1
		hop['expiry'] = 400
		hop['fee'] = str(1)
		hop['fee_msat'] = str(1000)

		hop['amt_to_forward'] = str(total_amt - i)
		hop['amt_to_forward_msat'] = str(1000*(total_amt - i))

	routes['routes'][0]['total_fees'] = str(len(routes['routes'][0]['hops']))
	routes['routes'][0]['total_amt'] = str(total_amt)
	routes['routes'][0]['total_amt_msat'] = str(total_amt*1000)
	routes['routes'][0]['total_fees_msat'] = str(len(routes['routes'][0]['hops'])*1000)
	return routes

def find_last_hop(first_node, last_node):
	# List all channels
	res = first_node.container.exec_run(listchannels())
	channels = json.loads(res.output.decode('utf-8'))

	for hop in channels['channels']:
		if hop['pub_key'] == last_node.pubkey:
			return make_hop(hop['pub_key'], hop['chan_id'])
	raise Execption('last node not found error')

def main():
	num_nodes = 3
	network = networkinitializer.setup(num_nodes, with_balance = True)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	alice = lnd_nodes[0]
	bob = lnd_nodes[1]
	carol = lnd_nodes[2]


	# Open connection from Alice to Bob and Bob to Carol and Coral to Alice

	res = alice.container.exec_run(createconnection(bob))
	print(res.output.decode('utf-8'))
	res = alice.container.exec_run(openchannel(bob, 100000))
	print(res.output.decode('utf-8'))

	res = bob.container.exec_run(createconnection(carol))
	print(res.output.decode('utf-8'))
	res = bob.container.exec_run(openchannel(carol, 100000))
	print(res.output.decode('utf-8'))

	res = carol.container.exec_run(createconnection(alice))
	print(res.output.decode('utf-8'))
	res = carol.container.exec_run(openchannel(alice, 100000))
	print(res.output.decode('utf-8'))

	# res = bob.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))
	# res = alice.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))
	# res = carol.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))

	# confirm the funding transactions; only 3 are needed for lnd
	bitcoind.container.exec_run(generatetoaddress(6))

	time.sleep(2)

	res = bob.container.exec_run(listchannels())
	print(res.output.decode('utf-8'))
	res = alice.container.exec_run(listchannels())
	print(res.output.decode('utf-8'))
	res = carol.container.exec_run(listchannels())
	print(res.output.decode('utf-8'))
	# Get invoice from alice
	# TODO: sleep substitute for actual pooling for nodes so that it is more accurate.
	# THis is wait time for network so that all payments are along the same route
	time.sleep(15)

	res = carol.container.exec_run(getinvoice(1000))
	pay_req = get_attr(res, 'pay_req')
	payment_hash = get_attr(res, 'r_hash')
	print(payment_hash)

	# We need to parse the structure of the queryroutes 
	res = alice.container.exec_run(queryroutes(carol, 1000))
	routes = json.loads(res.output.decode('utf-8'))

	# find_last_hop(); add last hop to routes
	print(routes)
	routes = create_all_but_one_edge_circle_route(routes, 1002)
	print(routes)
	last_hop = find_last_hop(alice, carol)
	routes['routes'][0]['hops'].append(last_hop)
	print(routes)
	# Feed the output of querypath and add last edge to the paths to complete the circle. 
	# Send payment back
	# print(sendtoroute(payment_hash, str(routes))) 
	print(sendtoroute(payment_hash, str(routes)))
	print(sendtoroute(payment_hash, json.dumps(routes)))
	res = alice.container.exec_run(sendtoroute(payment_hash, "\'" + json.dumps(routes) + "\'"))
	print(res.output.decode('utf-8'))

	bob.container.exec_run(listchannels())
	alice.container.exec_run(listchannels())
	carol.container.exec_run(listchannels())

	return

if __name__ == "__main__":
	main()
