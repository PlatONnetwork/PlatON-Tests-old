//auto create contract
#include <stdlib.h>
#include <string.h>
#include <platon/platon.hpp>

namespace platon {

    class ContractA : public Contract {
        public:
            ContractA(){}
            void init() {
            }

        PLATON_EVENT(contracta_event, const char * , const char *)
           
        public:

            void setStateA(const char *key,const char *value) {
                setState(key, value);
            }
           
            const char * getStateA(const char *key){
                std::string value;
                getState(key,value);
                return value.c_str();
            }

            int64_t returnInt(int64_t value){
                if (value == 0) {
                    return (std::numeric_limits<int64_t>::max)();
                }else {
                    return value;
                }
            }

            const char* returnString(const char* c){
                std::string str = c;
                str.append("test");
                return str.c_str(); 
            }

    };

}


PLATON_ABI(platon::ContractA, setAddr);
PLATON_ABI(platon::ContractA, getAddr);
PLATON_ABI(platon::ContractA, setState);
PLATON_ABI(platon::ContractA, getState);
PLATON_ABI(platon::ContractA, getOrigin);
//platon autogen begin
extern "C" { 
void init() {
platon::ContractA ContractA_platon;
ContractA_platon.init();
}

}
//platon autogen end