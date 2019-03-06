import networkinitializer
from ln_test_framework.lndctl import *

def main():
	num_nodes = 2
	network = networkinitializer.setup(num_nodes)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	# create connection
	res = lnd_nodes[1].container.exec_run(createconnection(lnd_nodes[0]))
	print(res)

	# create funding transaction

	# send payments

if __name__ == "__main__":
	main()