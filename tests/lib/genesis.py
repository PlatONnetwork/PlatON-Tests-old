class Genesis:
    class __Config:
        def __init__(self, config):
            self.__config = config
            self.cbft = self.__Cbft(config["cbft"])

        @property
        def chain_id(self):
            return self.__config["chainId"]

        # def __dict__(self):
            # self.__config["chainId"] = self.chain_id
            # self.__config["cbft"] = self.cbft.__dict__()
            # return self.__config

        class __Cbft:
            def __init__(self, cbft_cfg):
                self.__cbft_cfg = cbft_cfg

            # def __dict__(self):
            #     self.__cbft_cfg[""]

            @property
            def initial_nodes(self):
                return self.__cbft_cfg["initialNodes"]

            @property
            def epoch(self):
                return self.__cbft_cfg["epoch"]

            @property
            def amount(self):
                return self.__cbft_cfg["amount"]

            @property
            def validator_mode(self):
                return self.__cbft_cfg["validatorMode"]

            @property
            def period(self):
                return self.__cbft_cfg["period"]

    class __EconomicModel:
        def __init__(self, economic_model_cfg):
            self.__economic_model_cfg = economic_model_cfg
            self.common = self.__Common(economic_model_cfg["Common"])
            self.staking = self.__Staking(economic_model_cfg["Staking"])
            self.slashing = self.__Slashing(economic_model_cfg["Slashing"])
            self.gov = self.__Gov(economic_model_cfg["Gov"])
            self.reward = self.__Reward(economic_model_cfg["Reward"])
            self.inner_acc = self.__InnerAcc(economic_model_cfg["InnerAcc"])

        class __Common:
            def __init__(self, common_cfg):
                self.__common_cfg = common_cfg

            @property
            def expected_minutes(self):
                return self.__common_cfg["ExpectedMinutes"]

            @property
            def validataor_count(self):
                return self.__common_cfg["ValidatorCount"]

            @property
            def additional_cycle_time(self):
                return self.__common_cfg["AdditionalCycleTime"]

        class __Staking:
            def __init__(self, staking_cfg):
                self.__staking_cfg = staking_cfg

            @property
            def stake_threshold(self):
                return self.__staking_cfg["StakeThreshold"]

            @property
            def minimum_threshould(self):
                return self.__staking_cfg["MinimumThreshold"]

            @property
            def epoch_validator_num(self):
                return self.__staking_cfg["EpochValidatorNum"]

            @property
            def hesitate_ratio(self):
                return self.__staking_cfg["HesitateRatio"]

            @property
            def effective_ratio(self):
                return self.__staking_cfg["EffectiveRatio"]

            @property
            def un_stake_freeze_ratio(self):
                return self.__staking_cfg["UnStakeFreezeRatio"]

            @property
            def passive_un_delegate_freeze_ratio(self):
                return self.__staking_cfg["PassiveUnDelegateFreezeRatio"]

            @property
            def active_un_delegate_freeze_ratio(self):
                return self.__staking_cfg["ActiveUnDelegateFreezeRatio"]

        class __Slashing:
            def __init__(self, slashing_cfg):
                self.__slashing_cfg = slashing_cfg

            @property
            def pack_amount_abnormal(self):
                return self.__slashing_cfg["PackAmountAbnormal"]

            @property
            def duplicate_sign_high_slashing(self):
                return self.__slashing_cfg["DuplicateSignHighSlashing"]

            @property
            def number_of_block_reward_for_slashing(self):
                return self.__slashing_cfg["NumberOfBlockRewardForSlashing"]

            @property
            def evidence_valid_epoch(self):
                return self.__slashing_cfg["EvidenceValidEpoch"]

        class __Gov:
            def __init__(self, gov_cfg):
                self.__gov_cfg = gov_cfg

            @property
            def version_proposal_vote_duration_seconds(self):
                return self.__gov_cfg["VersionProposalVote_DurationSeconds"]

            @property
            def version_proposal_active_consensus_rounds(self):
                return self.__gov_cfg["VersionProposalActive_ConsensusRounds"]

            @property
            def version_proposal_support_rate(self):
                return self.__gov_cfg["VersionProposal_SupportRate"]

            @property
            def text_proposal_vote_duration_seconds(self):
                return self.__gov_cfg["TextProposalVote_DurationSeconds"]

            @property
            def text_proposal_vote_rate(self):
                return self.__gov_cfg["TextProposal_VoteRate"]

            @property
            def text_proposal_support_rate(self):
                return self.__gov_cfg["TextProposal_SupportRate"]

            @property
            def cancel_proposal_vote_rate(self):
                return self.__gov_cfg["CancelProposal_VoteRate"]

            @property
            def cancel_proposal_support_rate(self):
                return self.__gov_cfg["CancelProposal_SupportRate"]

        class __Reward:
            def __init__(self, reward_cfg):
                self.__reward_cfg = reward_cfg

            @property
            def new_block_rate(self):
                return self.__reward_cfg["NewBlockRate"]

            @property
            def platon_foundation_year(self):
                return self.__reward_cfg["PlatONFoundationYear"]

        class __InnerAcc:
            def __init__(self, inner_acc_cfg):
                self.__inner_acc_cfg = inner_acc_cfg

            @property
            def platon_fund_account(self):
                return self.__inner_acc_cfg["PlatONFundAccount"]

            @property
            def platon_fund_balance(self):
                return self.__inner_acc_cfg["PlatONFundBalance"]

            @property
            def CDF_account(self):
                return self.__inner_acc_cfg["CDFAccount"]

            @property
            def CDF_balance(self):
                return self.__inner_acc_cfg["CDFBalance"]

    def __init__(self, data):
        self.data = data
        self.config = self.__Config(data["config"])
        self.economic_model = self.__EconomicModel(data["EconomicModel"])
        self.alloc = data["alloc"]

    def __dict__(self):
        self.data["config"] = self.config.__dict__
        self.data["EconomicModel"] = self.economic_model.__dict__
        self.data["alloc"] = self.alloc
        return self.data


if __name__ == "__main__":
    def props_with_(obj):
        pr = {}
        for name in dir(obj):
            value = getattr(obj, name)
            if not name.startswith('__') and not callable(value):
                pr[name] = value
        return pr

    from common.load_file import LoadFile
    from conf.settings import GENESIS_FILE
    data = LoadFile(GENESIS_FILE).get_data()
    genesis = Genesis(data)
    print(genesis.config.chain_id)
    print(genesis.config.cbft.period)
    print(genesis.economic_model.common.additional_cycle_time)
    print(genesis.__dict__())