import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
def main():
	num_nodes = 2
	network = networkinitializer.setup(num_nodes, with_balance = True)

	bitcoind = network.bitcoind_node
	lnd_nodes = network.lnd_nodes

	alice = lnd_nodes[0]
	bob = lnd_nodes[1]

	bob.container.exec_run(createconnection(alice))
	
	bob.container.exec_run(openchannel(alice, 10000000))
	
	# printnodebalance(alice)
	# printnodebalance(bob)

	# confirm the funding transactions; only 3 are needed for lnd
	bitcoind.container.exec_run(generatetoaddress(6))
	bob.container.exec_run(listchannels())
	alice.container.exec_run(listchannels())
	# Get invoice from alice
	for i in range(0,100):
		if i %5 ==0:
			print("iter",i)
		res = alice.container.exec_run(getinvoice(100))
		pay_req = get_attr(res, 'pay_req')
		# print(pay_req)

		# Send payment back
		res = bob.container.exec_run(sendpayment(pay_req))
		# print(res.output.decode('utf-8'))
		# time.sleep(1)

	bob.container.exec_run(listchannels())
	alice.container.exec_run(listchannels())

	time.sleep(2)
	# printnodebalance(alice)
	# printnodebalance(bob)
	return

if __name__ == "__main__":
	main()
