# ln_measurement

1) Start bitcoind in regtest mode. In our expiriment all the LN nodes will be connected to single bitcoind as the backend although in real life they maybe onnected via different bitcoind. The result should not differ via this simplification

2) The implementation for LN is lnd cloned from https://github.com/lightningnetwork/lnd/ based on master release because of some new features which were not present in the latest release. TODO: Check if the results differ after releases.

