#include <vector>
#include <stdlib.h>
#include <platon/platon.hpp>
#include <platon/storagetype.hpp>

namespace platon
{
	char KEY_NAME[] = "ABCD";
	class matmul : public Contract
	{
	public:
		//std::vector<std::vector<int64_t>> d;
		Int64<KEY_NAME> s;
		int64_t n = 12;
	public:
		matmul() {}

		/// 初始化虚方法，仅会在合约发布时执行一次
		/// 示例：初始化时存入基本数据
		virtual void init()
		{
			//*s = 0;
			//platon::println("init work");
		}

		/// 定义事件及参数类型
		/// 参数1：事件名称，参数2：调用时传入参数类型，此处为字符串
		PLATON_EVENT(create, const char *,int64_t);


	public:
		std::vector<std::vector<int64_t> > math(std::vector<std::vector<int64_t> > x, std::vector<std::vector<int64_t> > y)
		{
			std::vector<std::vector<int64_t> > c(n, std::vector<int64_t>(n));
			std::vector<std::vector<int64_t> > d(n, std::vector<int64_t>(n));
			for (int i = 0; i < y[0].size(); i++)
			{
				for (int j = 0; j < y.size(); j++)
				{
					c[i][j]=y[j][i];
				}
			}
			for (int i = 0; i < x.size(); i++)
			{
				for (int j = 0; j < y[0].size(); j++)
				{
					d[i][j] = 0;
				}
			}
			for (int i = 0; i < x.size(); i++)
			{
				for (int j = 0; j < y[0].size(); j++)
				{
					int64_t ss = 0;
					std::vector<int64_t> xi = x[i];
					std::vector<int64_t> cj = c[j];
					for (int k = 0; k < x.size(); k++)
					{
						ss += xi[k] * cj[k];
						d[i][j] = ss;
					}
				}
			}
			return d;
		}
		void set(int64_t input)
		{
			int64_t n = input;
			int64_t tmp = (int64_t)n/2;
			std::vector<std::vector<int64_t> > a(n, std::vector<int64_t>(n));
			std::vector<std::vector<int64_t> > b(n, std::vector<int64_t>(n));
			std::vector<std::vector<int64_t> > f(n, std::vector<int64_t>(n));
			for (int64_t i = 0; i < n; i++) {
				for (int64_t j = 0; j < n; j++) {
					a[i][j] = (tmp * (i - j) * (i + j));
					platon::println(a[i][j]);
				}
			}
			b = a;
			f = math(a,b);
			*s = f[n/2][n / 2];
			platon::println("s is :");
			platon::println(*s);
			PLATON_EMIT_EVENT(create, "set success", *s);
		}

		int64_t get() const
		{
			return s.get();
		}

	};
};

PLATON_ABI(platon::matmul, set)
PLATON_ABI(platon::matmul, get)


//platon autogen begin
extern "C" { 
void set(long long input) {
platon::matmul matmul_platon;
matmul_platon.set(input);
}
long long get() {
platon::matmul matmul_platon;
return matmul_platon.get();
}
void init() {
platon::matmul matmul_platon;
matmul_platon.init();
}

}
//platon autogen end