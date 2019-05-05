import json
import networkx as nx
import matplotlib.pyplot as plt
import os
import shutil

data_dir = '../data/'
graph_dir = '../graph/'

def init_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)

init_dir(graph_dir)

def build(file):
    f = open(data_dir + file)
    data = json.loads(f.read())
    nodes = data['nodes']
    edges = data['edges']

    print("Number of nodes ", len(nodes))
    print("Number of edges", len(edges))

    G = nx.MultiDiGraph()
    for node in nodes:
        G.add_nodes_from([(node['pub_key'], node)])

    # print(G.node['02000b1f8a0eac1a299c2594f60055151a1d67bad2c37e09be4fcdc519d7ebe722']['alias'])

    total_cap = 0

    for edge in edges:
        channel_id = edge['channel_id']
        chan_point = edge['chan_point']
        last_update = edge['last_update']
        capacity = edge['capacity']
        total_cap+=int(capacity)

        node1_pub = edge['node1_pub']
        node2_pub = edge['node2_pub']
        # print(node1_pub)
        # print(node2_pub)

        node1_policy = edge['node1_policy']
        node2_policy = edge['node2_policy']

        G.add_edge(node1_pub, node2_pub, fee_policy=node1_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)
        G.add_edge(node2_pub, node1_pub, fee_policy=node2_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)

    _deg = nx.degree(G)
    deg = [(_deg[node] + 1) for node in G.nodes()]

    # nx.draw_random(G, node_size=deg, width=0.1, arrows=False)
    # print(f"Save snapshot to {graph_dir}{file[:-5]}.eps")
    # plt.savefig(f"{graph_dir}{file[:-5]}.eps")
    print(total_cap, "total_capacity")

# testnet_file = '2019_4_14_15_42_3.json'
# build(testnet_file)
build("temp.txt")
build("temp2.txt")
build("temp3.txt")
# mainnet_file = '2019_4_16_11_42_1.json'
# build(mainnet_file)
