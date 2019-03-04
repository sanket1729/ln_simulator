FROM ubuntu:16.04

RUN apt-get update && apt-get install -qy git
RUN apt-get install -qy build-essential
RUN apt-get install -qy libboost-all-dev
RUN apt-get install -qy libssl-dev libdb++-dev libdb-dev libminiupnpc-dev
RUN apt-get install -qy autoconf libtool pkg-config bsdmainutils libevent-dev libzmq3-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN apt-get update
RUN apt-get install -qy software-properties-common
RUN add-apt-repository ppa:bitcoin/bitcoin
RUN apt-get update
RUN apt-get install -qy libdb4.8-dev libdb4.8++-dev

RUN git clone https://github.com/bitcoin/bitcoin
WORKDIR bitcoin

RUN ./autogen.sh
RUN ./configure
RUN make

EXPOSE 18443
EXPOSE 18444
EXPOSE 28332
EXPOSE 28333
VOLUME /root/.bitcoin

ADD bitcoin.conf /root/.bitcoin/bitcoin.conf
CMD ["./src/bitcoind" ,"-regtest" ,"-debug"]
