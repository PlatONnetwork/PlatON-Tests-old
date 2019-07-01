#include <string>
#include <platon/platon.hpp>
#include <platon/storagetype.hpp>
#include <vector>

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
			*sum = 100;
		}

		/// 定义事件及参数类型
		/// 参数1：事件名称，参数2：调用时传入参数类型，此处为字符串
		PLATON_EVENT(NotifyWithCode, int64_t, const char *);


	public:
		void set(int64_t len)
		{
			*sum = 0;
			std::vector<std::int64_t> result;
			std::int64_t sumy;
			for (int64_t i = 0; i < len; i++) {
				if (i == 0 || i == 1) {
					result.push_back(1);
				}
				else {
					result.push_back(result[i - 2] + result[i - 1]);
					//platon::println(result[i]);
				}
			}
			//platon::println(result[10]);
			sumy = 0;
			for (int64_t j = 0; j < result.size(); j++) {
				sumy += result[j];
			}
			*sum = sumy;
			//platon::println("sum is :");
			//platon::println(*sum);
			PLATON_EMIT_EVENT(NotifyWithCode, *sum, "set success.");
		}

		/// @dev 获取账户余额
		int64_t get() const
		{
		    platon::println("sum is :");
		    platon::println(sum.get());
			return sum.get();
		}
	};
};


PLATON_ABI(platon::Fibonacci, set)
PLATON_ABI(platon::Fibonacci, get)
//platon autogen begin
extern "C" { 
void set(long long len) {
platon::Fibonacci Fibonacci_platon;
Fibonacci_platon.set(len);
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