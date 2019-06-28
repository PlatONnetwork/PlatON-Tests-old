# Test Case Dir

该文件夹用于存放所有测试用例，用例测试文件需要以test开头，

测试用例最基本的写法为
```python

import pytest


class TestCase():

    def setup(self):
        print("setup: 每个用例开始前执行")

    def teardown(self):
        print("teardown: 每个用例结束后执行")

    def setup_class(self):
        print("setup_class：所有用例执行之前")

    def teardown_class(self):
        print("teardown_class：所有用例结束后执行")

    def setup_method(self):
        print("setup_method:  每个用例开始前执行")

    def teardown_method(self):
        print("teardown_method:  每个用例结束后执行")

    def test_one(self):
        print("正在执行----test_one")
        x = "this"
        assert 'h' in x


def setup_module():
    print("setup_module：整个.py模块只执行一次")
    print("比如：所有用例开始前只打开一次浏览器")


def teardown_module():
    print("teardown_module：整个.py模块只执行一次")
    print("比如：所有用例结束只最后关闭浏览器")


def setup_function():
    print("setup_function：每个用例开始前都会执行")


def teardown_function():
    print("teardown_function：每个用例结束后都会执行")


def test_one():
    print("正在执行----test_one")
    x = "this"
    assert 'h' in x


def test_two():
    print("正在执行----test_two")
    x = "hello"
    assert hasattr(x, 'check')


def test_three():
    print("正在执行----test_three")
    a = "hello"
    b = "hello world"
    assert a in b


if __name__ == "__main__":
    pytest.main(["-s", "test_example.py"])

```
当然，pytest中也有更高级的前置处理器，需要的请[参阅](https://docs.pytest.org/en/latest/fixture.html#fixtures)