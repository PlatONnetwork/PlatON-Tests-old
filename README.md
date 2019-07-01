# PlatON-Tests
This project is an automated test project of the PaltON-Go. see: https://github.com/PlatONnetwork/PlatON-Go

### Run test:
windows环境变量,需要先把./utils/ethkey和./utils/pubkey目录分别添加至环境变量中。

在项目目录中执行以下命令
```js
python run.py --node='./deploy/node/4_node.yml' --case='all'

```
查看使用方式
```js
python run.py -h
```


### Dir introduce:
- [case](docs/case_example.md)
- common：主要包含一些公共使用的方法
- conf：用于全局测试配置
- data：一些必要的测试依赖文件，或者是数据驱动用例的数据
- [deploy](docs/deploy.md)
- docs：一些文档
- utils：基础库
