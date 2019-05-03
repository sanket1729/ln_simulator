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

def generate_path(send_amt, path):
	hops = []

	height = get_height()
	cltv = height
	total_amt_msat = send_amt * milli
	total_fees_msat = 0

	i = 0
	for edge in reversed(path):
		u, v, attr = edge[2]

		fee_policy = attr['fee_policy']

		min_htlc = fee_policy['min_htlc']
		cltv += min_htlc

		fee_base_msat = fee_policy['fee_base_msat']
		fee_rate_milli_msat = fee_policy['fee_rate_milli_msat']

		fee_msat = 0
		if i > 0:
			fee_msat = calc_fee(total_amt_msat, fee_base_msat, fee_rate_milli_msat)

		fee_sat = fee_msat // milli

		hop = {}
		hop['chan_id'] = attr['channel_id']
		hop['chan_capacity'] = attr['capacity']
		hop['amt_to_forward'] = total_amt_msat // milli
		hop['fee'] = fee_sat
		hop['expiry'] = cltv
		hop['amt_to_forward_msat'] = total_amt_msat
		hop['fee_msat'] = fee_msat
		hop['pub_key'] = u

		hops.append(hop)

		total_fees_msat += fee_msat
		total_amt_msat += total_fees_msat

		i += 1

	routes = {}
	routes['total_fees'] = total_fees_msat // milli
	routes['total_amt'] = total_amt_msat // milli
	routes['hops'] = hops
	routes['total_fees_msat'] = total_fees_msat
	routes['total_amt_msat'] = total_amt_msat

	return routes

def main():
	# source = get_source()
	# target = get_target()
	with open('../analysis/result/paths.txt', 'r') as f:
		input = f.readline()
		paths = literal_eval(input)
	for _path in paths:
		path = generate_path(_path)
	# find_min_balance(source, target, path)


if __name__ == "__main__":
	main()
