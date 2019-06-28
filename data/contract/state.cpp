// 状态相关 合约
#include <stdlib.h>
#include <string.h>
#include <string>

#include <platon/platon.hpp>
#include <platon/deployedcontract.hpp>

namespace platon {
    class StateContract : public platon::Contract {
         
		
		public:
            StateContract(){}
            
			/// 初始化虚方法，仅会在合约发布时执行一次
			/// 示例：初始化时存入基本数据
			virtual void init(){}

			PLATON_EVENT(TRANSFER, const char *,int64_t)
		
        public:
            // 内置函数验证获取

            // 获取区块hash
			const char* getBlockHash(int blockHeight) const 
			{						
				h256 hash = blockHash(blockHeight);
				print("get block hash:", hash.toString(), "\n");
				return hash.toString().c_str();
			}

			// 获取旷工账户
			const char* getCoinbase() const 
			{						
				h160 addr = coinbase();
				print("get coinbase address:", addr.toString(), "\n");
				return addr.toString().c_str();
			}

            // 
			const char* getOrigin() const 
			{						
				h160 oriAddr = origin();
				print("get origin address: ", oriAddr.toString(), "\n");
				return oriAddr.toString().c_str();
			}

			// 获取合约调用者   caller用delegateCall测试多层调用
			const char* getCaller() const 
			{						
				h160 callerAddr = caller();
				print("get caller address: ", callerAddr.toString(), "\n");
				return callerAddr.toString().c_str();
			}

			// 调用者时候发送的value 
			const char* getCallValue() const 
			{						
				u256 value = callValue();
				print("get caller address: ", value, "\n");
				return value.convert_to<std::string>().c_str();
			}


		    // 获取当前合约地址
			const char* getContractAddr(int blockHeight) const 
			{						
				platon::h160 contract_addr = platon::address();
				print("get contract address: ", contract_addr.toString(), "\n");
				return contract_addr.toString().c_str();
			}
			
			// 获取合约账户余额，是否应该增加接口查询某个地址余额？
			const char* getBalance() const 
			{						
				platon::u256 b = platon::balance();
				return b.convert_to<std::string>().c_str();
			}

			const char* getSha3(const char *src) const 
			{				
				h256 dest = sha3((byte*)src, strlen(src));
				return dest.toString().c_str();
			} 

			const char* getSha3str(const char *src) const 
			{				
				h256 dest2 = sha3(src);
				return dest2.toString().c_str();
			}        

            //调用该方法是
			int64_t transfer(const char *addr, uint64_t amount) 
			{				
				Address toAddr(addr, true);
				int64_t res = callTransfer(toAddr,amount);
				PLATON_EMIT_EVENT(TRANSFER,addr,amount);
			    return res;
			}        

    };
}

PLATON_ABI(platon::StateContract, getBlockHash);
PLATON_ABI(platon::StateContract, getCoinbase);
PLATON_ABI(platon::StateContract, getOrigin);
PLATON_ABI(platon::StateContract, getCaller);
PLATON_ABI(platon::StateContract, getCallValue);
PLATON_ABI(platon::StateContract, getContractAddr);
PLATON_ABI(platon::StateContract, getBalance);
PLATON_ABI(platon::StateContract, getSha3);
PLATON_ABI(platon::StateContract, getSha3str);
PLATON_ABI(platon::StateContract, transfer);




