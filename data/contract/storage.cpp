#include <stdlib.h>
#include <string.h>
#include <string>

#include <platon/platon.hpp>
#include <platon/deployedcontract.hpp>

PLATON_EVENT(notify, int32_t);

namespace platon {
    class StorageContract : public platon::Contract {
         
    
		public:
            StorageContract(){}
            
			/// 初始化虚方法，仅会在合约发布时执行一次
			/// 示例：初始化时存入基本数据
			virtual void init(){}

            //key-value
            PLATON_EVENT(SET_INT, const char*, uint64_t);
            PLATON_EVENT(SET_STRING, const char*, const char*);

        public:
            // 存储
			void setStateInt(const char *key, const uint64_t value) {
                print("setStateInt key:", key, " value:", value);
                setState(key, value);
                uint64_t result;
                getState(key,result);
                PlatonAssert(value == result, "set value error!");
                PLATON_EMIT_EVENT(SET_INT, key,value);
            }
 
            uint64_t getStateInt(const char *key){
                print("getStateInt key:", key);
                uint64_t  result;
                getState(key, result);
                return result;
            }

            void setStateString(const char *key, const char *value) {
                print("setStateString key:", key, " value:", value);
                setState(key, value);
                std::string result;
                getState(key,result);
                PlatonAssert(value == result, "set string error!");
                PLATON_EMIT_EVENT(SET_STRING, key,value);
            }
 
            const char* getStateString(const char *key){
                print("getStateString key:", key);
                std::string result;
                getState(key, result);
                return result.c_str();
            }

    };
}

PLATON_ABI(platon::StorageContract, setStateInt);
PLATON_ABI(platon::StorageContract, getStateInt);
PLATON_ABI(platon::StorageContract, setStateString);
PLATON_ABI(platon::StorageContract, getStateString);
//platon autogen begin
extern "C" { 
void setStateInt(const char * key,unsigned long long value) {
platon::StorageContract StorageContract_platon;
StorageContract_platon.setStateInt(key,value);
}
unsigned long long getStateInt(const char * key) {
platon::StorageContract StorageContract_platon;
return StorageContract_platon.getStateInt(key);
}
void setStateString(const char * key,const char * value) {
platon::StorageContract StorageContract_platon;
StorageContract_platon.setStateString(key,value);
}
const char * getStateString(const char * key) {
platon::StorageContract StorageContract_platon;
return StorageContract_platon.getStateString(key);
}
void init() {
platon::StorageContract StorageContract_platon;
StorageContract_platon.init();
}

}
//platon autogen end