#include <string>
#include <platon/platon.hpp>
#include <platon/storagetype.hpp>

namespace platon
{
	char KEY_NAME[] = "ABCD";
	char KEY_NAME_A[] = "A";
	char KEY_NAME_B[] = "B";
	char KEY_NAME_C[] = "C";
	class inputtest : public Contract
	{
	public:
		Int64<KEY_NAME> sum;
		String<KEY_NAME_A> a;
		//String<KEY_NAME_B> b;
		//String<KEY_NAME_C> c;

	public:
		inputtest() {}

		/// 初始化虚方法，仅会在合约发布时执行一次
		/// 示例：初始化时存入基本数据
		virtual void init()
		{
			*sum = 0;
		}

		/// 定义事件及参数类型
		/// 参数1：事件名称，参数2：调用时传入参数类型，此处为字符串
		PLATON_EVENT(NotifyWithCode, int64_t, const char *);


	public:
		void set(int64_t input)
		{
			*sum = input;
			//*a = x;
			//b = y;
			//c = z;
			//a = a + 101;
			platon::println("input is :");
			platon::println(input);
			platon::println("sum is :");
			platon::println(*sum);
			PLATON_EMIT_EVENT(NotifyWithCode, input,"set success");
		
		}

		/// @dev 获取账户余额
		int64_t get() const
		{	
			return sum.get();
		}
		//const char * geta()
		//{
		//	return a->c_str();
		//}
	};
};


PLATON_ABI(platon::inputtest, set)
PLATON_ABI(platon::inputtest, get)
//PLATON_ABI(platon::inputtest, geta)
//platon autogen begin
extern "C" { 
void set(long long input) {
platon::inputtest inputtest_platon;
inputtest_platon.set(input);
}
long long get() {
platon::inputtest inputtest_platon;
return inputtest_platon.get();
}
void init() {
platon::inputtest inputtest_platon;
inputtest_platon.init();
}

}
//platon autogen end