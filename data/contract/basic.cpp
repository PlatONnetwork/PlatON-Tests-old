// 基础合约(数据类型（入参、出参)、数据结构、算术运算) 
#include <stdlib.h>
#include <string.h>
#include <string>
#include <stack>
#include <vector>         
#include <deque>
#include <queue>
#include <array>
#include <set>
#include <map>
#include <tuple>

#include <platon/platon.hpp>

using namespace std;
namespace wasm {
    class BasicContract : public platon::Contract {
        public:
            BasicContract(){}

            /// 实现父类: platon::Contract 的虚函数
            /// 该函数在合约首次发布时执行，仅调用一次
            void init() 
            {
                platon::println("init success...");
            }

            // 定义事件
            PLATON_EVENT(notify, uint64_t, const char *);
        public:
            // 数组 int8_t -123
            void test_set_arr_int8(int8_t a, int8_t b, int8_t c) {
                platon::println("test_set_arr_int8 input is: ", a, b, c);
                array<int8_t, 3> int8Arr;
                int8Arr[0] = a;
                int8Arr[1] = b;
                int8Arr[2] = c;
                if (3 != int8Arr.size()) {
                    platon::println("test_set_arr_int8 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < int8Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", int8Arr[i]);
                    }
                    platon::setState("int8Arr", int8Arr);
                    platon::println("test_set_arr_int8 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                } 
            }

            int8_t test_get_arr_int8() {
                array<int8_t, 3> int8Arr;
                platon::getState("int8Arr", int8Arr);
                if (int8Arr.empty()) {
                    platon::println("test_get_arr_int8 fail.");
                    return 0;
                }
                platon::println("test_get_arr_int8 success..");
                return int8Arr[0];
            }

            // uint8_t 127
            void test_set_arr_uint8(uint8_t a, uint8_t b, uint8_t c) {
                platon::println("test_set_arr_uint8 input is: ", a, b, c);
                array<uint8_t, 3> uint8Arr;
                uint8Arr[0] = a;
                uint8Arr[1] = b;
                uint8Arr[2] = c;
                if (3 != uint8Arr.size()) {
                    platon::println("test_set_arr_uint8 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < uint8Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", uint8Arr[i]);
                    }
                    platon::setState("uint8Arr", uint8Arr);
                    platon::println("test_set_arr_uint8 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            int8_t test_get_arr_uint8() {
                array<uint8_t, 3> uint8Arr;
                platon::getState("uint8Arr", uint8Arr);
                if (uint8Arr.empty()) {
                    platon::println("test_get_arr_uint8 fail.");
                    return 0;
                }
                platon::println("test_get_arr_uint8 success..");
                return uint8Arr[0];
            }

            // int16_t -1234
            void test_set_arr_int16(int16_t a, int16_t b, int16_t c) {
                platon::println("test_set_arr_int16 input is: ", a, b, c);
                array<int16_t, 3> int16Arr;
                int16Arr[0] = a;
                int16Arr[1] = b;
                int16Arr[2] = c;
                if (3 != int16Arr.size()) {
                    platon::println("test_set_arr_int16 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {  
                    for (int i = 0; i < int16Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", int16Arr[i]);
                    } 
                    platon::setState("int16Arr", int16Arr);
                    platon::println("test_set_arr_int16 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            int16_t test_get_arr_int16() {
                array<int16_t, 3> int16Arr;
                platon::getState("int16Arr", int16Arr);
                if (int16Arr.empty()) {
                    platon::println("test_get_arr_int16 fail.");
                    return 0;
                }
                platon::println("test_get_arr_int16 success..");
                return int16Arr[0];
            }

            // uint16_t 12345
            void test_set_arr_uint16(uint16_t a, uint16_t b, uint16_t c) {
                platon::println("test_set_arr_uint16 input is: ", a, b, c);
                array<uint16_t, 3> uint16Arr;
                uint16Arr[0] = a;
                uint16Arr[1] = b;
                uint16Arr[2] = c;
                if (3 != uint16Arr.size()) {
                    platon::println("test_set_arr_uint16 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < uint16Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", uint16Arr[i]);
                    }
                    platon::setState("uint16Arr", uint16Arr);
                    platon::println("test_set_arr_uint16 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            uint16_t test_get_arr_uint16() {
                array<uint16_t, 3> uint16Arr;
                platon::getState("uint16Arr", uint16Arr);
                if (uint16Arr.empty()) {
                    platon::println("test_get_arr_uint16 fail.");
                    return 0;
                }
                platon::println("test_get_arr_uint16 success..");
                return uint16Arr[0];
            }

            // int32_t -12345566
            void test_set_arr_int32(int32_t a, int32_t b, int32_t c) {
                platon::println("test_set_arr_int32 input is: ", a, b, c);
                array<int32_t, 3> int32Arr;
                int32Arr[0] = a;
                int32Arr[1] = b;
                int32Arr[2] = c;
                if (3 != int32Arr.size()) {
                    platon::println("test_set_arr_int32 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < int32Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", int32Arr[i]);
                    }
                    platon::setState("int32Arr", int32Arr);
                    platon::println("test_set_arr_int32 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            int32_t test_get_arr_int32() {
                array<int32_t, 3> int32Arr;
                platon::getState("int32Arr", int32Arr);
                if (int32Arr.empty()) {
                    platon::println("test_get_arr_int32 fail.");
                    return 0;
                }
                platon::println("test_get_arr_int32 success..");
                return int32Arr[0];
            }

            // uint32_t 12345676
            void test_set_arr_uint32(uint32_t a, uint32_t b, uint32_t c) {
                platon::println("test_set_arr_uint32 input is: ", a, b, c);
                array<uint32_t, 3> uint32Arr;
                uint32Arr[0] = a;
                uint32Arr[1] = b;
                uint32Arr[2] = c;
                if (3 != uint32Arr.size()) {
                    platon::println("test_set_arr_uint32 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < uint32Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", uint32Arr[i]);
                    }
                    platon::setState("uint32Arr", uint32Arr);
                    platon::println("test_set_arr_uint32 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            uint32_t test_get_arr_uint32() {
                array<uint32_t, 3> uint32Arr;
                platon::getState("uint32Arr", uint32Arr);
                if (uint32Arr.empty()) {
                    platon::println("test_get_arr_uint32 fail.");
                    return 0;
                }
                platon::println("test_get_arr_uint32 success..");
                return uint32Arr[0];
            }

            // int64_t -1234342432444
            void test_set_arr_int64(int64_t a, int64_t b, int64_t c) {
                platon::println("test_set_arr_int64 input is: ", a, b, c);
                array<int64_t, 3> int64Arr;
                int64Arr[0] = a;
                int64Arr[1] = b;
                int64Arr[2] = c;
                if (3 != int64Arr.size()) {
                    platon::println("test_set_arr_int64 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < int64Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", int64Arr[i]);
                    }
                    platon::setState("int64Arr", int64Arr);
                    platon::println("test_set_arr_int64 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            int64_t test_get_arr_int64() {
                array<int64_t, 3> int64Arr;
                platon::getState("int64Arr", int64Arr);
                if (int64Arr.empty()) {
                    platon::println("test_get_arr_int64 fail.");
                    return 0;
                }
                platon::println("test_get_arr_int64 success..");
                return int64Arr[0];
            }

            // uint64_t 1234342432444 
            void test_set_arr_uint64(uint64_t a, uint64_t b, uint64_t c) {
                platon::println("test_set_arr_uint64 input is: ", a, b, c);
                array<uint64_t, 3> uint64Arr;
                uint64Arr[0] = a;
                uint64Arr[1] = b;
                uint64Arr[2] = c;
                if (3 != uint64Arr.size()) {
                    platon::println("test_set_arr_uint64 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < uint64Arr.size(); ++i) {
                        platon::println("loop the arr i is: ", uint64Arr[i]);
                    }
                    platon::setState("uint64Arr", uint64Arr);
                    platon::println("test_set_arr_uint64 success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            uint64_t test_get_arr_uint64() {
                array<uint64_t, 3> uint64Arr;
                platon::getState("uint64Arr", uint64Arr);
                if (uint64Arr.empty()) {
                    platon::println("test_get_arr_uint64 fail.");
                    return 0;
                }
                platon::println("test_get_arr_uint64 success..");
                return uint64Arr[0];
            }

            // 栈 double
            void test_set_stack_double(double a, double b, double c) {
                platon::println("test_set_stack_double input is: ", a);
                stack<double> doubleStack;
                doubleStack.push(a);
                doubleStack.push(b);
                doubleStack.push(c);
                if (3 != doubleStack.size()) {
                    platon::println("test_set_stack_double fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    platon::setState("doubleStack", doubleStack);
                    platon::println("test_set_stack_double success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            double test_get_stack_double() {
                stack<double> doubleStack;
                platon::getState("doubleStack", doubleStack);
                if (doubleStack.empty()) {
                    platon::println("test_get_stack_double fail.");
                    return 0.0;
                }
                platon::println("test_get_stack_double success..");
                return doubleStack.top();
            }   

             // 队列 double
            void test_set_queue_double(double a, double b, double c) {
                platon::println("test_set_queue_double input is: ", a, b, c);
                queue<double> doubleQueue;
                doubleQueue.push(a);
                doubleQueue.push(b);
                doubleQueue.push(c);
                if (3 != doubleQueue.size()) {
                    platon::println("test_set_queue_double fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    platon::setState("doubleQueue", doubleQueue);
                    platon::println("test_set_queue_double success..");
                    PLATON_EMIT_EVENT(notify, 1, "success"); 
                }              
            }

            double test_get_queue_double() {
                queue<double> doubleQueue;
                platon::getState("doubleQueue", doubleQueue);
                if (doubleQueue.empty()) {
                    platon::println("test_get_queue_double fail.");
                    return 0.0;
                } 
                platon::println("test_get_queue_double success..");
                return doubleQueue.front();
            }

            // 字典 char for
            void test_set_map_char(char a, char b, char c) {
                platon::println("test_set_map_char input is: ", a, b, c);
                map<int, char> charMap;
                charMap[0] = a;
                charMap[1] = b;
                charMap[2] = c;
                if (3 != charMap.size()) {
                    platon::println("test_set_map_char fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");
                } else {
                    for (int i = 0; i < charMap.size(); ++i) {
                        platon::println("loop the map i is: ", charMap[i]);
                    }
                    platon::setState("charMap", charMap);
                    platon::println("test_set_map_char success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");
                }
            }

            char test_get_map_char() {
                map<int, char> charMap;
                platon::getState("charMap", charMap);
                if (charMap.count(1) > 0) {
                    platon::println("test_get_map_char success..");
                    return charMap[1];
                } else {
                    platon::println("test_get_map_char fail.");
                    return 'A';
                }
            }

            // 向量 int for
            void test_set_vector_int(int a, int b, int c) {
                platon::println("test_set_vector_int input is: ", a, b, c);
                vector<int> inVector;
                inVector.insert(inVector.begin(), a);
                inVector.insert(inVector.begin()+1, b);
                inVector.insert(inVector.begin()+2, c);
                if (3 != inVector.size()) {
                    platon::println("test_set_vector_int fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail");   
                } else {
                    for (size_t i = 0; i < inVector.size(); i++) {
                        platon::println("loop the vector i is: ", inVector.at(i));
                    }
                    platon::setState("inVector", inVector);
                    platon::println("test_set_vector_int success..");
                    PLATON_EMIT_EVENT(notify, 1, "success");    
                }
            }

            int test_get_vector_int() {
                vector<int> inVector;
                platon::getState("inVector", inVector);
                if (0 == inVector.size()) {
                    platon::println("test_get_vector_int fail.");
                    return 0;
                } else {
                    platon::println("test_get_vector_int success..");
                    return inVector.front();  
                }
            }

            // 集合 char
            void test_set_set_uint32(uint32_t a, uint32_t b, uint32_t c) {
                platon::println("test_set_set_uint32 input is: ", a, b, c);
                set<uint32_t> uint32Set;
                uint32Set.insert(a);
                platon::println("test_set_set_uint32 the size of the set is: ", uint32Set.size());
                uint32Set.clear();
                if(!uint32Set.empty()) {
                    platon::println("test_set_set_uint32 fail.");
                    PLATON_EMIT_EVENT(notify, 0, "fail"); 
                } else {
                    platon::println("test_set_set_uint32 has cleared");
                    uint32Set.insert(b);
                    uint32Set.insert(c);
                    if (2 != uint32Set.size()) {
                        platon::println("test_set_set_uint32 fail.");
                        PLATON_EMIT_EVENT(notify, 0, "fail"); 
                    } else {
                        platon::println("test_set_set_uint32 the begin of the set is: ", *uint32Set.begin());
                        platon::println("test_set_set_uint32 the end of the set is: ", *uint32Set.end());
                        platon::setState("uint32Set", uint32Set);
                        platon::println("test_set_set_uint32 success..");
                        PLATON_EMIT_EVENT(notify, 1, "success");
                    }
                }
            }

            uint32_t test_get_set_uint32() {
                set<uint32_t> uint32Set;
                platon::getState("uint32Set", uint32Set);
                if (0 == uint32Set.size()) {
                    platon::println("test_get_set_uint32 fail.");
                    return 0;
                } else {
                    platon::println("test_get_set_uint32 success..");
                    return *uint32Set.begin();
                }
            }

            // 链表 long
            long test_list_long(long a, long b, long c) {
                platon::println("test_list_long input is: ", a, b, c);
                list<long> longList;
                longList.push_front(a);
                longList.push_front(b);
                longList.push_front(c);
                if (3 != longList.size()) {
                    platon::println("test_list_long fail.");   
                    PLATON_EMIT_EVENT(notify, 0, "fail");  
                }
                platon::println("test_list_long success, return front()..");
                PLATON_EMIT_EVENT(notify, 1, "success");
                return longList.front();
            }

            // 算术运算符
            void test_arithmetic_operation(int a, int b) {
                int c;
                platon::println("test_arithmetic_operation input is: ", a, b);
                c = a + b;
                platon::println("test_arithmetic_operation add result is: ", c);
                c = a - b;
                platon::println("test_arithmetic_operation sub result is: ", c);
                c = a * b;
                platon::println("test_arithmetic_operation mul result is: ", c);
                c = a / b;
                platon::println("test_arithmetic_operation div result is: ", c);
                c = a % b;
                platon::println("test_arithmetic_operation mod result is: ", c);
                int d = 10;   //  测试自增、自减
                c = d++;
                platon::println("test_arithmetic_operation 10++ result is: ", c);
                d = 10;    // 重新赋值
                c = d--;
                platon::println("test_arithmetic_operation 10-- result is: ", c);
            }

            // 关系运算符
            void test_relational_operation(int a, int b) {
                platon::println("test_relational_operation input is: ", a, b);
                if ( a == b ) {
                    platon::println("test_relational_operation a == b");
                } else {
                    platon::println("test_relational_operation a != b");
                }
                if ( a < b ) {
                    platon::println("test_relational_operation a < b");
                } else {
                    platon::println("test_relational_operation a > b");
                }
                if ( a > b ) {
                    platon::println("test_relational_operation a > b");
                } else {
                    platon::println("test_relational_operation a < b");
                }
                /* 改变 a 和 b 的值 */
                int c;
                c = a;
                a = b;
                b = c;
                if ( a <= b ) {
                    platon::println("test_relational_operation a <= b");
                }
                if ( b >= a ) {
                    platon::println("test_relational_operation a >= b");
                }
            }

            // 逻辑运算符
            void test_logic_operation(int a, int b) {
                platon::println("test_logic_operation input is: ", a, b);
                int c ;
                if ( a && b ) {
                    platon::println("test_logic_operation a&&b is true");
                } else {
                    platon::println("test_logic_operation a&&b is false");
                }
                if ( a || b ) {
                    platon::println("test_logic_operation a || b is true");
                } else {
                    platon::println("test_logic_operation a || b is false");
                }
                if ( !(a && b) ) {
                    platon::println("test_logic_operation !(a && b) is true");
                } else {
                    platon::println("test_logic_operation !(a && b) is false");
                }
            }

            // 位运算符
            void test_bit_operation(int a, int b) {
                platon::println("test_bit_operation input is: ", a, b);
                /*unsigned int a = 60;      // 60 = 0011 1100  
                unsigned int b = 13;      // 13 = 0000 1101*/
                int c = 0;           

                c = a & b;             // 12 = 0000 1100
                platon::println("test_bit_operation a & b is: ", c);

                c = a | b;             // 61 = 0011 1101
                platon::println("test_bit_operation a | b is: ", c);

                c = a ^ b;             // 49 = 0011 0001
                platon::println("test_bit_operation a ^ b is: ", c);

                c = ~a;                // -61 = 1100 0011
                platon::println("test_bit_operation ~a is: ", c);

                c = a << 2;            // 240 = 1111 0000
                platon::println("test_bit_operation a << 2 is: ", c);

                c = a >> 2;            // 15 = 0000 1111
                platon::println("test_bit_operation a >> 2 is: ", c);
            }

            // 赋值运算符
            void test_assignment_operation(int a) {
                platon::println("test_assignment_operation input is: ", a);
                int c;

                c =  a;
                platon::println("test_assignment_operation c = a : ", c);

                c +=  a;
                platon::println("test_assignment_operation c += a : ", c);

                c -=  a;
                platon::println("test_assignment_operation c -= a : ", c);

                c *=  a;
                platon::println("test_assignment_operation c *= a : ", c);

                c /=  a;
                platon::println("test_assignment_operation c /= a : ", c);

                c  = 200;
                c %=  a;
                platon::println("test_assignment_operation c is 200 and c %= a : ", c);

                c <<=  2;
                platon::println("test_assignment_operation c <<= 2 : ", c);

                c >>=  2;
                platon::println("test_assignment_operation c >>= 2 : ", c);

                c &=  2;
                platon::println("test_assignment_operation c &= 2 : ", c);

                c ^=  2;
                platon::println("test_assignment_operation c ^= 2 : ", c);

                c |=  2;
                platon::println("test_assignment_operation c |= 2 : ", c);
            }

            // test_calc
            int test_calc(uint64_t a, uint64_t b, uint64_t c, uint64_t p) {
                double y = (a+b+c) / 3.0;
                double z = (y+p) / 2.0;

                double arr[3];
                arr[0] = z - a;
                arr[1] = z - b;
                arr[2] = z - c;

                double min = arr[0];
                int idx = -1;
                if (min >= 0.0f) {
                    idx = 1;
                }
                for (int i = 1; i < 3; i++) {
                    if (arr[i] >= 0.0f && (arr[i] < min || min < 0.0f))  {
                        min = arr[i];
                        idx = i+1;
                        continue;
                    }
                }
                platon::println("arr[0]", arr[0], "arr[1]", arr[1], "arr[2]", arr[2], "idx", idx);
                if (idx < 0){
                    PLATON_EMIT_EVENT(notify, 0, "success");
                    return 0;
                }

                PLATON_EMIT_EVENT(notify, idx, "success");
                return idx;
            }

            // flase_loop
            int test_false_loop() {
                int i = 0;
                while(true) {
                    i++;
                }
                return i;
            }
    };
}

// 生成ABI文件供外部调用
PLATON_ABI(wasm::BasicContract, test_set_arr_int8);
PLATON_ABI(wasm::BasicContract, test_get_arr_int8);
PLATON_ABI(wasm::BasicContract, test_set_arr_uint8);
PLATON_ABI(wasm::BasicContract, test_get_arr_uint8);
PLATON_ABI(wasm::BasicContract, test_set_arr_int16);
PLATON_ABI(wasm::BasicContract, test_get_arr_int16);
PLATON_ABI(wasm::BasicContract, test_set_arr_uint16);
PLATON_ABI(wasm::BasicContract, test_get_arr_uint16);
PLATON_ABI(wasm::BasicContract, test_set_arr_int32);
PLATON_ABI(wasm::BasicContract, test_get_arr_int32);
PLATON_ABI(wasm::BasicContract, test_set_arr_uint32);
PLATON_ABI(wasm::BasicContract, test_get_arr_uint32);
PLATON_ABI(wasm::BasicContract, test_set_arr_int64);
PLATON_ABI(wasm::BasicContract, test_get_arr_int64);
PLATON_ABI(wasm::BasicContract, test_set_arr_uint64);
PLATON_ABI(wasm::BasicContract, test_get_arr_uint64);
PLATON_ABI(wasm::BasicContract, test_set_stack_double);
PLATON_ABI(wasm::BasicContract, test_get_stack_double);
PLATON_ABI(wasm::BasicContract, test_set_queue_double);
PLATON_ABI(wasm::BasicContract, test_get_queue_double);
PLATON_ABI(wasm::BasicContract, test_set_map_char);
PLATON_ABI(wasm::BasicContract, test_get_map_char);
PLATON_ABI(wasm::BasicContract, test_set_vector_int);
PLATON_ABI(wasm::BasicContract, test_get_vector_int);
PLATON_ABI(wasm::BasicContract, test_set_set_uint32);
PLATON_ABI(wasm::BasicContract, test_get_set_uint32);
PLATON_ABI(wasm::BasicContract, test_list_long);
PLATON_ABI(wasm::BasicContract, test_arithmetic_operation);
PLATON_ABI(wasm::BasicContract, test_relational_operation);
PLATON_ABI(wasm::BasicContract, test_logic_operation);
PLATON_ABI(wasm::BasicContract, test_bit_operation);
PLATON_ABI(wasm::BasicContract, test_assignment_operation);
PLATON_ABI(wasm::BasicContract, test_calc);
PLATON_ABI(wasm::BasicContract, test_false_loop);
//platon autogen begin
extern "C" { 
void test_set_arr_int8(char a,char b,char c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_int8(a,b,c);
}
char test_get_arr_int8() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_int8();
}
void test_set_arr_uint8(unsigned char a,unsigned char b,unsigned char c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_uint8(a,b,c);
}
char test_get_arr_uint8() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_uint8();
}
void test_set_arr_int16(short a,short b,short c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_int16(a,b,c);
}
short test_get_arr_int16() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_int16();
}
void test_set_arr_uint16(unsigned short a,unsigned short b,unsigned short c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_uint16(a,b,c);
}
unsigned short test_get_arr_uint16() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_uint16();
}
void test_set_arr_int32(long a,long b,long c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_int32(a,b,c);
}
long test_get_arr_int32() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_int32();
}
void test_set_arr_uint32(unsigned long a,unsigned long b,unsigned long c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_uint32(a,b,c);
}
unsigned long test_get_arr_uint32() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_uint32();
}
void test_set_arr_int64(long long a,long long b,long long c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_int64(a,b,c);
}
long long test_get_arr_int64() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_int64();
}
void test_set_arr_uint64(unsigned long long a,unsigned long long b,unsigned long long c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_arr_uint64(a,b,c);
}
unsigned long long test_get_arr_uint64() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_arr_uint64();
}
void test_set_stack_double(double a,double b,double c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_stack_double(a,b,c);
}
double test_get_stack_double() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_stack_double();
}
void test_set_queue_double(double a,double b,double c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_queue_double(a,b,c);
}
double test_get_queue_double() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_queue_double();
}
void test_set_map_char(char a,char b,char c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_map_char(a,b,c);
}
char test_get_map_char() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_map_char();
}
void test_set_vector_int(int a,int b,int c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_vector_int(a,b,c);
}
int test_get_vector_int() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_vector_int();
}
void test_set_set_uint32(unsigned long a,unsigned long b,unsigned long c) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_set_set_uint32(a,b,c);
}
unsigned long test_get_set_uint32() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_get_set_uint32();
}
long test_list_long(long a,long b,long c) {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_list_long(a,b,c);
}
void test_arithmetic_operation(int a,int b) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_arithmetic_operation(a,b);
}
void test_relational_operation(int a,int b) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_relational_operation(a,b);
}
void test_logic_operation(int a,int b) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_logic_operation(a,b);
}
void test_bit_operation(int a,int b) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_bit_operation(a,b);
}
void test_assignment_operation(int a) {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.test_assignment_operation(a);
}
int test_calc(unsigned long long a,unsigned long long b,unsigned long long c,unsigned long long p) {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_calc(a,b,c,p);
}
int test_false_loop() {
wasm::BasicContract BasicContract_platon;
return BasicContract_platon.test_false_loop();
}
void init() {
wasm::BasicContract BasicContract_platon;
BasicContract_platon.init();
}

}
//platon autogen end