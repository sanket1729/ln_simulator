import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time

def main():
	num_good_nodes = 2
	num_grief_nodes = 1
	network = networkinitializer.setup(num_good_nodes, num_grief_nodes, with_balance = True)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	alice = lnd_nodes[0]
	bob = lnd_nodes[2]
	carol = lnd_nodes[1]


	# Open connection from Alice to Bob and Bob to Carol.

	res = alice.container.exec_run(createconnection(bob))
	print(res.output.decode('utf-8'))
	res = alice.container.exec_run(openchannel(bob, 100000))
	print(res.output.decode('utf-8'))

	res = bob.container.exec_run(createconnection(carol))
	print(res.output.decode('utf-8'))
	res = bob.container.exec_run(openchannel(carol, 100000))
	print(res.output.decode('utf-8'))

	# res = bob.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))
	# res = alice.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))
	# res = carol.container.exec_run(listchannels())
	# print(res.output.decode('utf-8'))

	# confirm the funding transactions; only 3 are needed for lnd
	bitcoind.container.exec_run(generatetoaddress(6))

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
	print(pay_req)

	# Send payment back
	res = alice.container.exec_run(sendpayment(pay_req))
	print(res.output.decode('utf-8'))

	bob.container.exec_run(listchannels())
	alice.container.exec_run(listchannels())
	carol.container.exec_run(listchannels())

	return

if __name__ == "__main__":
	main()
