import json
"""
'{
    "routes": [
        {
            "total_fees": "1",
            "total_amt": "2",
            "hops": [
                {
                    "chan_id": "359540302348288",
                    "chan_capacity": "100000",
                    "amt_to_forward": "1",
                    "fee": "1",
                    "expiry": 381,
                    "amt_to_forward_msat": "1000",
                    "fee_msat": "1000",
                    "pub_key": "02d35cb4e7552382ba77f359e0590dad101c05ac746a0ab8bb6ada12b730bacf15"
                },
                {
                    "chan_id": "359540302479360",
                    "chan_capacity": "100000",
                    "amt_to_forward": "1",
                    "fee": "0",
                    "expiry": 381,
                    "amt_to_forward_msat": "1000",
                    "fee_msat": "0",
                    "pub_key": "02f8c14bdf90d49dae88c4573f7d70bfb2c4d3bc25401894fb08f4cfc565924d8b"
                },
                {
                    "chan_id": "359540302413824",
                    "chan_capacity": "100000",
                    "amt_to_forward": "1",
                    "fee": "0",
                    "expiry": 381,
                    "amt_to_forward_msat": "1000",
                    "fee_msat": "0",
                    "pub_key": "0217531a8acb54b2fad4215f318f82dea72976fbb7d8a600806bea5b97c8e5f84a"
                }
            ],
            "total_fees_msat": "1000",
            "total_amt_msat": "2000"
        }
    ]
}'
"""
class lndroute():
	def __init__(self, total_fees, total_amt, hops, total_fees_msat, total_amt_msat):
		


class lndhop():
	def __init__(self, chan_id, chan_capacity, amt_to_forward, fee, expiry, amt_to_forward_msat, fee_msat, pub_key):
		self.chan_id = chan_id
		self.chan_capacity = chan_capacity
		self.amt_to_forward = amt_to_forward
		self.fee = fee
		self.expiry = expiry
		self.amt_to_forward_msat = amt_to_forward_msat
		self.fee_msat = fee_msat
		self.pub_key = pub_key
