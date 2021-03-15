# Test Farmewo

## Project structure

**1. root**

- pytest.ini: pytestTest the configuration file, see [pytest.ini](https://docs.pytest.org/en/latest/reference/customize.html).

- conftest.py: Customize the test command line, deploy the test environment, download the failure log, and so on.

**2. common**

- Project public methods, including logging, configuration file reading, connecting to linux server, establishing web3 connection, binary package download, etc.

**3. conf**

- Environment deployment configuration, please see the file notes for details.

**4. deploy**

- Deployment file storage path, used with conf.

**5. environment**
Deployment environment script, consisting of five classes: TestConfig, TestEnvironment, Account, Server, Node.

- TestConfig: Deployment environment configuration, test environment global configuration.
- Account: Test account management class for testing, account generation, transfer, etc.
- Server: Server management class for deployment, management server dependencies, and compressed file management.
- TestEnvironment: Test environment class, used to manage the test environment, start the node, close the node, restart the node, get the node, get the account, and so on.
- Node: Node class, used to manage nodes, with basic node information, node connections, node running status, node start and stop, and so on.

**6. tests**

- Test case storage directory

**7. tests/lib**

- Client: The test case mainly calls objects, like a medicine box, bringing the ENV, LIB, and SDK together
- Config: Contains some configuration of PPOS, PIP, and Economic for test cases
- genesi：A wrapper class for genesis.json
- Utils: Test cases public method
- The rest of the classes are secondary packages for sdk
