import networkinitializer
from ln_test_framework.lndctl import *
from ln_test_framework.utils import *
from ln_test_framework.bitcoindctl import *
import time
import json
import copy
import random
import secrets
import docker
from ast import literal_eval
import networkx as nx

client = docker.from_env()

milli = 1000

def get_source():
	for container in client.containers.list():
		if container.name == 'lnd_testnet_source':
			return container
	raise Exception("source not running")


def get_target():
	for container in client.containers.list():
		if container.name == 'lnd_testnet':
			return container
	raise Exception("target not running")


def find_min_balance(source, target, path):
	high = 2**24 - 1
	low = 0
	while low < high:
		print(low, high)
		amt = (low + high)//2

		#get a random hash
		payment_hash = secrets.token_hex(32)
		# print(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))
		res = source.exec_run(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))

		assert get_attr(res, 'payment_error') != ""
		assert get_attr(res, 'payment_preimage') == ""
		if msg_reached(target, payment_hash):
			low = amt + 1
		else:
			high = amt

	print(low, high)
	print("The maximum balance which can be sent via bob-carol channel is " + str(low - 1 ))
	return


def msg_reached(node, hash):
	log = node.container.logs().decode('utf-8')
	return (hash in log)

def get_height(source):
	exec_res = source.exec_run(getinfo(chain='source_testnet'))
	return int(json.loads(exec_res.output.decode('utf-8')).get('block_height'))

def calc_fee(amt, fee_base_msat, fee_rate_milli_msat):
	fee = fee_base_msat + (amt * fee_rate_milli_msat) // (milli ** 2)
	return fee

def generate_path(send_amt, path, source):
	hops = []

	height = get_height(source)
	cltv = height
	total_amt_msat = send_amt * milli
	total_fees_msat = 0

	hops = []
	for i in range(len(path)):
		hops.append({})

	flag = False
	for i in reversed(range(len(path))):
		fee_msat = 0
		hops[i]['chan_id'] = path[i][2]['channel_id']
		hops[i]['chan_capacity'] = path[i][2]['capacity']
		if not flag:

			flag = True
		else:
			fee_policy = path[i + 1][2]['fee_policy']

			min_htlc = int(fee_policy['min_htlc'])
			cltv += min_htlc

			fee_base_msat = int(fee_policy['fee_base_msat'])
			fee_rate_milli_msat = int(fee_policy['fee_rate_milli_msat'])
			fee_msat = calc_fee(total_amt_msat, fee_base_msat, fee_rate_milli_msat)

		hops[i]['amt_to_forward'] = total_amt_msat // milli
		hops[i]['fee'] = fee_msat // milli
		hops[i]['expiry'] = cltv
		hops[i]['amt_to_forward_msat'] = total_amt_msat
		hops[i]['fee_msat'] = fee_msat
		hops[i]['pub_key'] = path[i][1]

		total_fees_msat += fee_msat
		total_amt_msat += fee_msat
    
	routes = {}
	routes['total_time_lock'] = cltv + int(path[0][2]['fee_policy']['min_htlc'])
	routes['total_fees'] = total_fees_msat // milli
	routes['total_amt'] = total_amt_msat // milli
	routes['hops'] = hops
	routes['total_fees_msat'] = total_fees_msat
	routes['total_amt_msat'] = total_amt_msat

	ret = {}
	ret['routes'] = routes
    
	return ret

def get_path(G, s, t, num):
    paths = []

    head = 0
    tail = 0
    q = []

    q.append(([s], []))
    tail += 1

    while head < tail and len(paths) < num:
        _nodes, _edges = q[head]
        end_node = _nodes[-1]
        head += 1

        for edge in G.edges(end_node, data=True):
            y = edge[1]
            if y == t:
                edges = _edges.copy()
                edges.append(edge)
                paths.append(edges)
                if len(paths) >= num:
                    break
            elif y not in _nodes:
                nodes = _nodes.copy()
                nodes.append(y)
                edges = _edges.copy()
                edges.append(edge)
                q.append((nodes, edges))
                tail += 1

    return paths

def build():
    f = open('../data/testnet/2019_5_2_8_42_5.json', 'r')
    data = json.loads(f.read())
    nodes = data['nodes']
    channels = data['edges']

    G = nx.MultiDiGraph()

    for node in nodes:
        G.add_nodes_from([(node['pub_key'], node)])

    for channel in channels:
        channel_id = channel['channel_id']
        chan_point = channel['chan_point']
        last_update = channel['last_update']
        channel['capacity'] = int(channel['capacity'])
        capacity = channel['capacity']

        node1_pub = channel['node1_pub']
        node2_pub = channel['node2_pub']

        node1_policy = channel['node1_policy']
        node2_policy = channel['node2_policy']

        G.add_edge(node1_pub, node2_pub, fee_policy=node1_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)
        G.add_edge(node2_pub, node1_pub, fee_policy=node2_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)

    nodes = ['02c7d9597510a71a33356c7c5cd1bc627e2fd348f73044183f97c5c81db76e38fb',
             '03a13a469bae4785e27fae24e7664e648cfdb976b97f95c694dea5e55e7d302846',
             '0270685ca81a8e4d4d01beec5781f4cc924684072ae52c507f8ebe9daf0caaab7b',
             '030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673']
    path = []
    for i in range(len(nodes) - 1):
        u = nodes[i]
        v = nodes[i + 1]
        edge = G.get_edge_data(u, v)[0]
        # edge = G.get_edge_data(v, u)[0]
        print(edge)
        path.append((u, v, edge))

    print(generate_path(1001, path))

    s = '02c7d9597510a71a33356c7c5cd1bc627e2fd348f73044183f97c5c81db76e38fb'
    t = '030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673'

    num = 3
    return get_path(G, s, t, num)

def main():
	source = get_source()
	target = get_target()
	with open('../analysis/result/paths.txt', 'r') as f:
		input = f.readline()
		paths = literal_eval(input)
	for _path in paths:
		path = generate_path(1000, _path, source)
		print(path)
		find_min_balance(source, target, path)


if __name__ == "__main__":
	main()
