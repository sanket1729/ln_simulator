import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *

def main():
	num_nodes = 2
	network = networkinitializer.setup(num_nodes, with_balance = True)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	alice = lnd_nodes[0]
	bob = lnd_nodes[1]

	bob.container.exec_run(createconnection(alice))
	
	bob.container.exec_run(openchannel(alice, 100000))
	
	# confirm the funding transactions; only 3 are needed for lnd
	bitcoind.container.exec_run(generatetoaddress(6))
	# Get invoice from alice
	alice.container.exec_run(getinvoice(1000))
	pay_req = get_attr(res, 'pay_req')

	# Send payment back
	res = bob.container.exec_run(sendpayment(pay_req))
	print(res.output.decode('utf-8'))
	return

if __name__ == "__main__":
	main()
