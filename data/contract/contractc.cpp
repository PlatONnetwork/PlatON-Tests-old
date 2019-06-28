//auto create contract
#include <stdlib.h>
#include <string.h>
#include <platon/platon.hpp>

 namespace platon {

    class ConctactC : public Contract {
        public:
            ConctactC(){}
            void init() {
            }

           std::string  contractAddr;  //被调用合约地址
           std::string  KEY_CONTRACT_ADDR = "contractAddr";

           PLATON_EVENT(ContractInvoke, const char* , uint8_t);
           PLATON_EVENT(SetContractAddr, const char*);
    
        public:
            void setAddr(const char *addr) {
                print("set invoke contract addr:", addr);
                setState(KEY_CONTRACT_ADDR.c_str(), addr);
                PLATON_EMIT_EVENT(SetContractAddr, addr);
            }
 
            const char* getAddr() {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                return contractAddr.c_str();
            }
           
             //调用contracta.cpp 存储某个k-v，之后调用getKey检测正确性
        	void testCall(const char *key,const char *value) {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                c.call("setStateA", key,value);
                std::string result = c.callString("getStateA",key);
                PlatonAssert(value == result.c_str(), "call error");
                PLATON_EMIT_EVENT(ContractInvoke,"Call Success",0);
            }

            //调用contracta.cpp 返回int
            int64_t testCallInt64(int64_t value) {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                int64_t i= c.callInt64("returnInt64",value);
                print_f("contractc callInt64 result i=% \n", i);
                return i;
            }

            //调用contracta.cpp 存储某个k-v，之后调用getKey检测正确性
            const char* testCallString(const char *key,const char *value) {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                std::string result = c.callString("returnStr",key,value);
                return result.c_str();
            }

            //调用contracta.cpp 返回
            void testDCall(const char *key,const char *value) {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                c.delegateCall("setStateA", key,value);
                std::string result = c.delegateCallString("getStateA",key);
                PlatonAssert(value == result.c_str(), "call error");
                PLATON_EMIT_EVENT(ContractInvoke,"delegateCall Success",0);
            }

            //调用contracta.cpp 返回int
            int64_t testDCallInt64() {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                int64_t i= c.delegateCallInt64("returnInt64");
                print_f("contractc delegateCallInt64 result i=% \n", i);
                return i;
            }

            //调用contracta.cpp 返回string
            const char* testDCallString() {
                getState(KEY_CONTRACT_ADDR.c_str(), contractAddr);
                DeployedContract c(contractAddr);
                std::string s = c.delegateCallString("returnStr");
                print_f("contractc delegateCallString result s=% \n", s);
                return s.c_str();
            }
    };

}

PLATON_ABI(platon::ConctactC, setAddr);
PLATON_ABI(platon::ConctactC, getAddr);
PLATON_ABI(platon::ConctactC, testCall);
PLATON_ABI(platon::ConctactC, testCallInt64);
PLATON_ABI(platon::ConctactC, testCallString);
PLATON_ABI(platon::ConctactC, testDCall);
PLATON_ABI(platon::ConctactC, testDCallInt64);
PLATON_ABI(platon::ConctactC, testDCallString);
//platon autogen begin
extern "C" { 
void setAddr(const char * addr) {
platon::ConctactC ConctactC_platon;
ConctactC_platon.setAddr(addr);
}
const char * getAddr() {
platon::ConctactC ConctactC_platon;
return ConctactC_platon.getAddr();
}
void testCall(const char * key,const char * value) {
platon::ConctactC ConctactC_platon;
ConctactC_platon.testCall(key,value);
}
long long testCallInt64(long long value) {
platon::ConctactC ConctactC_platon;
return ConctactC_platon.testCallInt64(value);
}
const char * testCallString(const char * key,const char * value) {
platon::ConctactC ConctactC_platon;
return ConctactC_platon.testCallString(key,value);
}
void testDCall(const char * key,const char * value) {
platon::ConctactC ConctactC_platon;
ConctactC_platon.testDCall(key,value);
}
long long testDCallInt64() {
platon::ConctactC ConctactC_platon;
return ConctactC_platon.testDCallInt64();
}
const char * testDCallString() {
platon::ConctactC ConctactC_platon;
return ConctactC_platon.testDCallString();
}
void init() {
platon::ConctactC ConctactC_platon;
ConctactC_platon.init();
}

}
//platon autogen end