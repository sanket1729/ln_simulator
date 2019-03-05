import docker
import sys
import time

from ln_test_framework.nodecontainer import *
from ln_test_framework.bitcoindctl import *

def main(n):
	client = docker.from_env()
	low_level_client = docker.APIClient()

	# 1) create an instance of bitcoind
	print("Starting bitcoind-backend")
	bitcoind = client.containers.run('bitcoind-lnd', name = "bitcoind-backend",detach=True)
	print("waiting 15 sec for bitcoind to start")
	time.sleep(15)
	bitcoind.exec_run(generatetoaddress(150))
	# 2) Create n instances of lnd
	lnd_containers = []
	print("Starting lnd containers")
	for i in range(0, n):
		lnd_containers.append(client.containers.run('lnd', name = "ln_node-" + str(i),detach=True))
	# 3) Get IP address and construct nodes for these containers
	return

if __name__ == "__main__":
	n =2
	if len(sys.argv) == 2:
		n = sys.argv[1] 
	main(n)	