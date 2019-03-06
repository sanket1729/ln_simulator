
class DockerNode:
	
	def __init__(self, ip_address , node_id, container):
		self.ip_address = ip_address
		self.node_id = node_id
		self.container = container

class BitcoindNode(DockerNode):

	def __init__(self, ip_address, node_id, container, name = None):
		super().__init__(ip_address, node_id, container)
		self.name = name

class LndNode(DockerNode):

	def __init__(self, ip_address, node_id, container, pubkey, name = None):
		super().__init__(ip_address, node_id, container)
		self.name = name
		self.pubkey = pubkey
