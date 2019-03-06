import docker
import sys
import time
import json

from ln_test_framework.nodecontainer import *
from ln_test_framework.bitcoindctl import *
from ln_test_framework.lndctl import *
from ln_test_framework.lnnetwork import *

def setup(n):
	client = docker.from_env()
	low_level_client = docker.APIClient()

	# 1) create an instance of bitcoind
	print("Starting bitcoind-backend")
	bitcoind_container = client.containers.run('bitcoind-lnd', name = "bitcoind-backend",detach=True)
	print("waiting 5 sec for bitcoind to start")
	time.sleep(5)
	print("Mining 150 blocks")
	bitcoind_container.exec_run(generatetoaddress(150))
	# print(x)
	

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
	time.sleep(5)
	print("waiting 5 sec for lnd_nodes to start")
	
	lnd_nodes = []
	for i in range(0,n):
		exec_res = lnd_containers[0].exec_run(getnewaddress())
		pubkey = json.loads(exec_res.output.decode('utf-8')).get('identity_pubkey')

		lnd_node_ip = low_level_client.inspect_container(lnd_containers[i].id)['NetworkSettings']['IPAddress']
		lnd_nodes.append(LndNode(ip_address = lnd_node_ip, node_id = lnd_containers[i].id, container = lnd_containers[i], pubkey = pubkey))
	
	#Print all info sanity
	print(bitcoind_node.node_id, bitcoind_node.ip_address)
	for i in range(0, n):
		print(lnd_nodes[i].node_id, lnd_nodes[i].ip_address, lnd_nodes[i].pubkey)

	net = LNnetwork(bitcoind_node, lnd_nodes)
	return net

if __name__ == "__main__":
	n =2
	if len(sys.argv) == 2:
		n = sys.argv[1] 
	setup(n)	
