# PlatON-Tests
This is an automated test project of the PaltON-Go.


## dependency

Install the python 3.7+, and execute the following command:

```shell
pip install -r requirements.txt
```

some libs rely on C++ 14, Please install them frist.

## Usage

### run all cases

```shell
pytest "tests" --nodeFile "node.yml"
```

### run at multi environment

```shell
pytest "tests" --nodeFile "node_1.yml,node_2.yml" -n 2
```

### Custom CLI

--nodeFile: Node configurat file, refer [[deploy.md](docs/deploy.md)].

--accountFile: Account file，refer [[deploy.md](deploy/accounts.yml)].

--platonUrl: Automatically download the platon.

--installDependency：Install the required dependencies for use during the first deployment.

--installSuperVisor：Install the supervisor during the first deployment.

--tmpDir: Specify cache dir, default in deploy/tmp.

--initChain: Whether to initialize the nodes, default ture.

--job: Use only when using CI.

ps: Refer to pytest for other commands