docker build -t bitcoind-lnd ./bitcoind/
docker build -t lnd ./lnd/
docker build -t lnd-grief ./lnd-grief/
python3 ./network_sim/ln_test_framework/stop_all_containers.py
