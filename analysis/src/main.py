import json
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

data_dir = '../data/'
testnet_dir = 'testnet/'
mainnet_dir = 'mainnet/'

graph_dir = '../graph/'

result_dir = '../result/'

milli = 1000

def check_connectivity(nodes, targets, threshold):
    head = 0
    tail = 0
    q = []

    q.append((nodes.copy(), targets.copy()))
    tail += 1

    while head < tail:
        _nodes, _targets = q[head]
        head += 1

        for edge in G.edges(nodes[-1], data=True):
            attr = edge[2]
            if 'capacity' in attr and attr['capacity'] < threshold:
                continue

            y = edge[1]
            if y in nodes:
                continue

            nodes = _nodes.copy()
            targets = _targets.copy()
            if y in targets:
                targets.remove(y)
                if len(targets) <= 0:
                    return True

            nodes.append(y)
            q.append((nodes, targets))
            tail += 1

    return False

def dfs(x, targets, nodes, edges, threshold, channel):
    global G, top

    nodes.append(x)

    res = []

    new_targets = targets.copy()

    if x == new_targets[-1]:
        del new_targets[-1]
        if len(new_targets) <= 0:
            res.append(edges)
            return res

    if x == channel['node1_pub']:
        edges.append(channel)
        res.extend(dfs(channel['node2_pub'], new_targets, nodes, edges, threshold, channel))
        del edges[-1]
    else:
        for edge in G.edges(x, data=True):
            attr = edge[2]
            if 'capacity' in attr.keys() and attr['capacity'] < threshold:
                continue

            y = edge[1]
            if y in nodes:
                continue

            if not check_connectivity(nodes, new_targets, threshold):
                continue

            edges.append(edge)
            res.extend(dfs(y, new_targets, nodes, edges, threshold, channel))
            del edges[-1]
            if len(res) >= top:
                return res

    del nodes[-1]

def find_path(channel):
    global s, t

    node1_pub = channel['node1_pub']
    node2_pub = channel['node2_pub']
    # find path : s -> node1_pub -> node2_pub -> t

    l = 0
    r = channel['capacity']
    while l < r:
        print('find_path', l, r)
        mid = (l + r) >> 1
        if dfs(s, [t, node2_pub, node1_pub], [], [], mid, channel):
            l = mid
        else:
            r = mid - 1

    return l, dfs(s, [t, node2_pub, node1_pub], [], [], l, channel)

def get_height():
    pass

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

    #test whether routes work
    #return True of False

def check_balance(balance, paths):
    for path in paths:
        if generate_path(balance, path):
            return True
    return False

def find_balance(min_cap, paths):
    l = 0
    r = min_cap
    while l < r:
        mid = (l + r) >> 1
        if check_balance(mid, paths):
            l = mid
        else:
            r = mid - 1
    return l

def draw_graph(G, file):
    _deg = nx.degree(G)
    deg = [(_deg[node] + 1) for node in G.nodes()]

    nx.draw_random(G, node_size=deg, width=0.1, arrows=False)
    print(f"Save snapshot to {graph_dir}{file[:-5]}.eps")
    plt.savefig(f"{graph_dir}{file[:-5]}.eps")

    for edge in G.edges(data=True):
        print(edge)
        break

def get_path():
    global G, s, t, num

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

    with open(result_dir + 'paths.txt', 'w') as f:
        f.write(str(paths))

    # for path in paths:
    #     min_cap = None
    #     for edge in path:
    #         attr = edge[2]
    #         cap = attr['capacity']
    #         if not min_cap or cap < min_cap:
    #             min_cap = cap
    #     find_balance(min_cap, paths)

def build(dir, file):
    global G, s, t, top, num

    f = open(data_dir + dir + file)
    data = json.loads(f.read())
    nodes = data['nodes']
    channels = data['edges']

    print(f"Node number: {len(nodes)}")
    print(f"Edge number: {len(channels)}")

    G = nx.MultiDiGraph()

    node_with_pub_ip = {}
    for node in nodes:
        pub_key = node['pub_key']
        G.add_nodes_from([(pub_key, node)])
        addresses = node['addresses']
        if len(addresses):
            # print(addresses)
            node_with_pub_ip[pub_key] = addresses
    print(f"nodes with pub ip: {len(node_with_pub_ip)}\n ratio is {len(node_with_pub_ip) / len(nodes)}")

    # print(G.node['02000b1f8a0eac1a299c2594f60055151a1d67bad2c37e09be4fcdc519d7ebe722']['alias'])

    cap = defaultdict(int)
    for channel in channels:
        channel_id = channel['channel_id']
        chan_point = channel['chan_point']
        last_update = channel['last_update']
        channel['capacity'] = int(channel['capacity'])
        capacity = channel['capacity']

        node1_pub = channel['node1_pub']
        node2_pub = channel['node2_pub']
        # print(node1_pub)
        # print(node2_pub)

        cap[f"{min(node1_pub, node2_pub)} {max(node1_pub, node2_pub)}"] += capacity

        node1_policy = channel['node1_policy']
        node2_policy = channel['node2_policy']

        G.add_edge(node1_pub, node2_pub, fee_policy=node1_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)
        G.add_edge(node2_pub, node1_pub, fee_policy=node2_policy, channel_id=channel_id, chan_point=chan_point, last_update=last_update, capacity=capacity)

    # for key, value in reversed(sorted(cap.items(), key=lambda e:e[1])):
    #     print(key, value)
    #     break
    # # draw_graph(G, file)
    # u = '0270685ca81a8e4d4d01beec5781f4cc924684072ae52c507f8ebe9daf0caaab7b'
    # # node_pubkey = '030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673'
    # # draw_single_node(node_pubkey, G)
    # for v in G[u]:
    #     if v in node_with_pub_ip:
    #         print(u, v, node_with_pub_ip[v], G.get_edge_data(u, v))

    s = '02c7d9597510a71a33356c7c5cd1bc627e2fd348f73044183f97c5c81db76e38fb'
    t = '030d815d7fe692edf238fa07aaad9e33da712e710033b7f5be3fc8f1386ea48673'

    top = 1
    for channel in channels:
        threshold, paths = find_path(channel)
        balance = find_balance(min(channel['capacity'], threshold), paths)

    # num = 3
    # get_path()

testnet_file = '2019_5_2_8_42_5.json'
build(testnet_dir, testnet_file)

# mainnet_file = '2019_4_16_11_42_1.json'
# build(mainnet_dir, mainnet_file)