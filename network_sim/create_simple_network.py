import docker
import sys
import time

from ln_test_framework.nodecontainer import *
from ln_test_framework.bitcoindctl import *
from ln_test_framework.lndctl import *

def main(n):
	client = docker.from_env()
	low_level_client = docker.APIClient()

	# 1) create an instance of bitcoind
	print("Starting bitcoind-backend")
	bitcoind_container = client.containers.run('bitcoind-lnd', name = "bitcoind-backend",detach=True)
	print("waiting 15 sec for bitcoind to start")
	time.sleep(15)
	print("Mining 150 blocks")
	x = bitcoind_container.exec_run(generatetoaddress(150))
	print(x)
	# 2) Create n instances of lnd
	lnd_containers = []
	print("Starting lnd containers")
	for i in range(0, n):
		lnd_containers.append(client.containers.run('lnd', name = "ln_node-" + str(i),detach=True))
	# 3) Get IP address and construct nodes for these containers
	
	# get bitcoind container info
	bitoind_ip = low_level_client.inspect_container(bitcoind_container.id)['NetworkSettings']['IPAddress']
	bitcoind_node = BitcoindNode(ip_address = bitoind_ip, node_id = "bitcoind", container = bitcoind_container)

	# get lnd container info
	lnd_nodes = []
	for i in range(0,n):
		lnd_node_ip = low_level_client.inspect_container(lnd_containers[i].id)['NetworkSettings']['IPAddress']
		lnd_nodes.append(LndNode(ip_address = lnd_node_ip, node_id = lnd_containers[i].id, container = lnd_containers[i]))
	
	print(bitcoind_node.node_id, bitcoind_node.ip_address)

	for i in range(0, n):
		print(lnd_nodes[i].node_id, lnd_nodes[i].ip_address)

	addr = getnewaddress()
	print(addr)
	temp = lnd_containers[1].exec_run("./lncli --no-macaroons --network=regtest getinfo")
	print(temp)
	temp = lnd_containers[0].exec_run(addr)
	print(temp)
	return

if __name__ == "__main__":
	n =2
	if len(sys.argv) == 2:
		n = sys.argv[1] 
	main(n)	