# Deploy

Deploy the Platon blockchain, only support ubuntu 18.04+, 


## Usage

Place platon into './deploy/bin', and specify the environment configuration file when you run the test case.


## node.yml 

```yml
consensus: 			# init node, optional
- host: 192.168.1.100 				# node`s ip，required
  username: test   				# node`s username，required
  password: test			    # node`s password，required
  id: 5b068ef1cfeef626d9ad131d08b889002a2f5c7306ff34c3032ad04fcc92fd234d0c7272014068eb998dae2abfe9f10271ed6731963b1cf22ec944abd8fb0f9e # node id，optional
  nodekey: 3314532da43158885d8db07e0b25dc0c194c8382c4fa5ce8c28a0b7c86cdec16 # node private key，optional
  blspubkey: e3797fad1041ecbd0b91b444de1f063ab74849a0fffa9fa9565ca2b0f78a1420a036d529be9f81576bcb836653436ac0e6eb91143b2e04cb1b0dc93da3ddf893 # bls public key，optional
  blsprikey: e4c7bb7918e474bff76b07361ec44b2d613fb9cfb58a296a90bcfbf7bace491f # bls private key，optional
  port: 16789 # node p2p port，optional
  rpcport: 6789 # node rpc port，optional
  wsport: 6790 # node web socket port，optional
- host: 10.10.8.237
  username: 
  password: 
noconsensus: # normal nodes, optional
- host: 192.168.1.200
  username: 
  password: 
  ```
