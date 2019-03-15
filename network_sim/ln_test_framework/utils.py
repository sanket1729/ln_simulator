import json
from ln_test_framework.lndctl import walletbalance

def get_attr(exec_res, attr):
	return json.loads(exec_res.output.decode('utf-8')).get(attr)

def printnodebalance(node):
	try:
		exec_res = node.container.exec_run(walletbalance())
	except AttributeError:
		exec_res = node.exec_run(walletbalance())
	print(exec_res.output.decode('utf-8'))
