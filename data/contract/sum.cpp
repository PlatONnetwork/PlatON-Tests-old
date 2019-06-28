#include <string>
#include <platon/platon.hpp>
#include <platon/storagetype.hpp>

namespace platon
{
	char KEY_NAME[] = "ABCD";

	class Fibonacci : public Contract
	{

	public:
		
		Int64<KEY_NAME> sum;

	public:
		Fibonacci() {}

		/// 初始化虚方法，仅会在合约发布时执行一次
		/// 示例：初始化时存入基本数据
		virtual void init()
		{
			*sum = 0;
			//platon::println("init work");
		}

		/// 定义事件及参数类型
		/// 参数1：事件名称，参数2：调用时传入参数类型，此处为字符串
		PLATON_EVENT(create, const char *);


	public:
		void set()
		{
			*sum += 1;
			//platon::println("sum is:");
			//platon::println(*sum);
			PLATON_EMIT_EVENT(create, "set success");
		}

		/// @dev 获取账户余额
		int64_t get() const
		{
			//platon::println("get sum:",*sum);
			return sum.get();
		}
	};
};


PLATON_ABI(platon::Fibonacci, set)
PLATON_ABI(platon::Fibonacci, get)
//platon autogen begin
extern "C" { 
void set() {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.set();
}
long long get() {
platon::Fibonacci Fibonacci_platon;
return Fibonacci_platon.get();
}
void init() {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.init();
}

}
//platon autogen end