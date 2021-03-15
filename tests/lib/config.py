import os
from conf.settings import BASE_DIR


class StakingConfig:
    def __init__(self, external_id, node_name, website, details):
        self.external_id = external_id
        self.node_name = node_name
        self.website = website
        self.details = details


class PipConfig:
    PLATON_NEW_BIN = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/platon"))
    PLATON_NEW_BIN1 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version1/platon"))
    PLATON_NEW_BIN2 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version2/platon"))
    PLATON_NEW_BIN3 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version3/platon"))
    PLATON_NEW_BIN4 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version4/platon"))
    PLATON_NEW_BIN8 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version8/platon"))
    PLATON_NEW_BIN9 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version9/platon"))
    PLATON_NEW_BIN6 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version6/platon"))
    PLATON_NEW_BIN7 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/newpackage/version7/platon"))
    PLATON_NEW_BIN0 = os.path.abspath(os.path.join(BASE_DIR, "deploy/bin/platon"))
    text_proposal = 1
    cancel_proposal = 4
    version_proposal = 2
    param_proposal = 3
    vote_option_yeas = 1
    vote_option_nays = 2
    vote_option_Abstentions = 3
    version1 = 67073
    version2 = 65536
    version3 = 65545
    version4 = 65792
    version5 = 65793
    version6 = 65801
    version7 = 66048
    version8 = 591617
    version9 = 526081
    version0 = 65536
    transaction_cfg = {"gasPrice": 3000000000000000, "gas": 1000000}


class EconomicConfig:
    # Year zero lock_pu release amount
    RELEASE_ZERO = 62215742.48691650
    # Year zero Initial issue
    TOKEN_TOTAL = 10250000000000000000000000000
    # Built in node Amount of pledge
    DEVELOPER_STAKING_AMOUNT = 1500000000000000000000000
    # PlatON Foundation Address
    FOUNDATION_ADDRESS = "lat1drz94my95tskswnrcnkdvnwq43n8jt6dmzf8h8"
    # Lock account account address
    FOUNDATION_LOCKUP_ADDRESS = "lat1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqp7pn3ep"
    # Pledged contract address
    STAKING_ADDRESS = "lat1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqzsjx8h7"
    # PlatON incentive pool account
    INCENTIVEPOOL_ADDRESS = "lat1zqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqrdyjj2v"
    # Remaining total account
    REMAIN_ACCOUNT_ADDRESS = "lat1rzw6lukpltqn9rk5k59apjrf5vmt2ncv8uvfn7"
    # Developer Foundation Account
    DEVELOPER_FOUNDATAION_ADDRESS = 'lat1kvurep20767ahvrkraglgd9t34w0w2g059pmlx'

    release_info = [{"blockNumber": 1600, "amount": 55965742000000000000000000},
                    {"blockNumber": 3200, "amount": 49559492000000000000000000},
                    {"blockNumber": 4800, "amount": 42993086000000000000000000},
                    {"blockNumber": 6400, "amount": 36262520000000000000000000},
                    {"blockNumber": 8000, "amount": 29363689000000000000000000},
                    {"blockNumber": 9600, "amount": 22292388000000000000000000},
                    {"blockNumber": 11200, "amount": 15044304000000000000000000},
                    {"blockNumber": 12800, "amount": 7615018000000000000000000}
                    ]
    fixed_gas = 70000