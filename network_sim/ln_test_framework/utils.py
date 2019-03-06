import json
def get_attr(exec_res, attr):
	return json.loads(exec_res.output.decode('utf-8')).get(attr)