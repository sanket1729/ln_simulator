import docker
import sys

from ln_test_framework.nodecontainer import *


def main(n):
	client = docker.from_env()
	low_level_client = docker.APIClient()

	# 1) create an instance of bitcoind
	print("Starting bitcoind-backend")
	bitcoind = client.containers.run('bitcoind-lnd', detach=True)
	# 2) Create n instances of lnd
	lnd_containers = []
	print("Starting lnd containers")
	for i in range(0, n):
		lnd_containers.append(client.containers.run('bitcoind-lnd', detach=True))
	# 3) Get IP address and construct nodes for these containers
	return

if __name__ == "__main__":
	n =2
	if len(sys.argv) == 2:
		n = sys.argv[1] 
	main(n)	