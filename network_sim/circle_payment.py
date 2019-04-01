import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
import json
# def find_last_hop(first_node, last_node):
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
	
	# Feed the output of querypath and add last edge to the paths to complete the circle. 
	# Send payment back
	print(routes)
	# print(sendtoroute(payment_hash, str(routes)))
	del routes['routes'][0]['total_time_lock']
	routes['routes'][0]['hops'][0]['expiry'] = 381
	routes['routes'][0]['hops'][1]['expiry'] = 381 
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
