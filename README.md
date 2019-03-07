# Simulator
Containerized version of featuting the following architecture. 


                                 --------------
                                |  bitcoind    |
                                 --------------
                  
                                 --------------            --------------
                                |     lnd     |           |      lnd     |
                                 --------------            --------------

# Dependancies
docker v-18
python3 docker library

```
pip3 install docker
```
# INSTALL instructions

PLEASE use this exact command. 
```
docker build -t bitcoind-lnd ./bitcoind/
docker build -t lnd ./lnd/
python3 ./network_sim/ln_test_framework/stop_all_containers.py
python3 ./network_sim/bi-directional.py
```


# ln_simulator

1) Start bitcoind in regtest mode. In our expiriment all the LN nodes will be connected to single bitcoind as the backend although in real life they maybe onnected via different bitcoind. The result should not differ via this simplification

2) The implementation for LN is lnd cloned from https://github.com/lightningnetwork/lnd/ based on master release because of some new features which were not present in the latest release. 
