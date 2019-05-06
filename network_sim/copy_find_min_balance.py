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
import threading

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


def find_min_balance(source, target, _path):
	print("starting")
	high = 2**24 - 1
	low = 0
	path = None
	while low < high:
		# print(low, high)
		amt = (low + high)//2

		#get a random hash
		# print(_path)
		path = generate_path(amt, _path, source)
		# print(path)
		payment_hash = secrets.token_hex(32)
		# print(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))
		res = source.exec_run(sendtoroute(payment_hash, "\'" + json.dumps(path) + "\'", chain = 'source_testnet'))
		# print(res)
		assert get_attr(res, 'payment_error') != ""
		assert get_attr(res, 'payment_preimage') == ""
		if msg_reached(target, payment_hash, oracle =True, res = res):
			low = amt + 1
		else:
			high = amt

	print(low, high)
	# print("The maximum balance which can be sent via bob-carol channel is " + str(low - 1 ))
	print(" Value for ", path, " is ", low - 1)
	return low - 1


def msg_reached(node, hash, oracle=False, res=None):
	if not oracle:
		log = node.logs().decode('utf-8')
		return (hash in log)
	else:
		return "UnknownPaymentHash" in get_attr(res, 'payment_error')

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
	ret['routes'] = [routes]

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

def abrev(pub_key):
	return pub_key[:8]

def check_connectivity(targets, nodes, threshold, G):
	# print(f"check connectivity nodes = {nodes} targets = {targets}")
	head = 0
	tail = 0
	q = []

	new_targets = targets.copy()

	if len(new_targets) <= 0:
		return True

	end_node = nodes[-1]
	q.append(end_node)
	tail += 1

	while head < tail:
		x = q[head]
		head += 1

		for edge in G.edges(x, data=True):
			_, y, attr = edge

			if attr['capacity'] < threshold:
				continue

			if y in nodes or y in q:
				continue

			if y in new_targets:
				new_targets.remove(y)
				if len(new_targets) <= 0:
					return True

			q.append(y)
			tail += 1

	# print(f"check failed")
	return False


def dfs(x, targets, nodes, edges, threshold, tgt_edge, G, top, res):
	# print(f"dfs x = {x}\ntargets = {targets}\nnodes = {nodes}")

	if len(targets) <= 0:
		res.append((nodes, edges))
		return

	if x == tgt_edge[0]:
		out_edges = [tgt_edge]
	else:
		out_edges = G.edges(x, data=True)

	for edge in out_edges:
		_, y, attr = edge

		if attr['capacity'] < threshold:
			continue

		if y in nodes:
			continue

		new_targets = targets.copy()
		if y in new_targets:
			if y == new_targets[-1]:
				del new_targets[-1]
			else:
				continue

		new_nodes = nodes.copy()
		new_nodes.append(y)
		if not check_connectivity(new_targets, new_nodes, threshold, G):
			continue

		new_edges = edges.copy()
		new_edges.append(edge)
		dfs(y, new_targets, new_nodes, new_edges, threshold, tgt_edge, G, top, res)
		if len(res) >= top:
			return

	return

def find_path(edge, G, s, t, top):
	u, v, attr = edge
	cap = attr['capacity']
	print(f"finding top {top} path containing edge {abrev(u)} -> {abrev(v)} with capacity {cap}")

	l = 0
	r = cap
	while l < r:
		mid = (l + r) >> 1
		# print(f"l = {l} r = {r} mid = {mid}")
		res = []
		dfs(s, [t, v, u], [s], [], mid, edge, G, top, res)
		if len(res) >= top:
			l = mid + 1
		else:
			r = mid - 1

	res = []
	dfs(s, [t, v, u], [s], [], l, edge, G, top, res)
	if len(res) < top:
		print(f"Less than top {top} paths")
		return None
	else:
		paths = []
		for nodes, edges in res:
			print(nodes)
			paths.append(edges)
		return l, paths

def get_connected_nodes(G, u):
	ret = []
	for _, v in G.edges(u):
		ret.append(v)
		# print(u, v, G[u][v][0]['capacity'])
	return ret

def build(source):
	f = open('./data/testnet/2019_5_5_9_42_6.json', 'r')
	data = json.loads(f.read())

	G = nx.MultiDiGraph()

	nodes = data['nodes']
	channels = data['edges']

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

	s = '02c7d9597510a71a33356c7c5cd1bc627e2fd348f73044183f97c5c81db76e38fb'
	t = '030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673'

	s_con = get_connected_nodes(G, s)
	t_con = get_connected_nodes(G, t)

	u = s_con[0]
	v = t_con[0]

	edges = G[u][v]
	edge = (u, v, edges[0])
	top = 2
	threshold, paths = find_path(edge, G, s, t, top)
	print(f"threshold {threshold}")
	return paths

	# num = 50
	# return get_path(G, s, t, num)

def main():
	source = get_source()
	target = get_target()
	paths = build(source)

	threads = []
	for _path in paths:
		t = threading.Thread(target = find_min_balance, args = (source, target, _path))
		threads.append(t)
		t.start()

	for t in threads:
		t.join()

if __name__ == "__main__":
	main()
