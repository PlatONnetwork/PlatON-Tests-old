#include <string>
#include <platon/platon.hpp>
#include <platon/storagetype.hpp>

namespace platon
{
	char KEY_NAME_X[] = "X";
	char KEY_NAME_Y[] = "Y";
	char KEY_NAME_STR1[] = "STR1";

	class Fibonacci : public Contract
	{

	public:
		
		Int64<KEY_NAME_X> x;
		Int16<KEY_NAME_Y> y;
		String<KEY_NAME_STR1> str1;

	public:
		Fibonacci() {}

		/// 初始化虚方法，仅会在合约发布时执行一次
		/// 示例：初始化时存入基本数据
		virtual void init()
		{
			*x = 50;
			*y = 3;
			*str1 = "hello beauty";
			//platon::println("init work");
		}

		/// 定义事件及参数类型
		/// 参数1：事件名称，参数2：调用时传入参数类型，此处为字符串
		PLATON_EVENT(create, const char *);


	public:
		void set_str(const char * a, const char * b)
		{
			*str1 += a;
			*str1 += b;
			//platon::println("sum is:");
			//platon::println(*sum);
			PLATON_EMIT_EVENT(create, "set_str success");
		}
		
		void set_number(int64_t a, int16_t c)
		{
			
			int64_t dd = 2;
			*x = (int64_t)(x * a - dd + a) / x * dd;
			
			int16_t d = 2;
			*y = (int16_t)(c * y + d) / d;
			
			PLATON_EMIT_EVENT(create, "set_number success");
		}

		/// @dev 获取账户余额
		const char * getstr()
		{
			return str1->c_str();
		}
		
		int64_t getx() const
		{
			return x.get();
		}
		
		int16_t gety() const
		{
			return y.get();
		}
	};
};


PLATON_ABI(platon::Fibonacci, set_str)
PLATON_ABI(platon::Fibonacci, set_number)
PLATON_ABI(platon::Fibonacci, getstr)
PLATON_ABI(platon::Fibonacci, getx)
PLATON_ABI(platon::Fibonacci, gety)
//platon autogen begin
extern "C" { 
void set_str(const char * a,const char * b) {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.set_str(a,b);
}
void set_number(long long a,short c) {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.set_number(a,c);
}
const char * getstr() {
platon::Fibonacci Fibonacci_platon;
return Fibonacci_platon.getstr();
}
long long getx() {
platon::Fibonacci Fibonacci_platon;
return Fibonacci_platon.getx();
}
short gety() {
platon::Fibonacci Fibonacci_platon;
return Fibonacci_platon.gety();
}
void init() {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.init();
}

}
//platon autogen end