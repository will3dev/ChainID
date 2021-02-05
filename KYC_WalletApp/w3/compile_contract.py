import json, os
from solcx import compile_source


contract = os.path.join(os.getcwd(), '..', '..', 'Contract', 'KYCWallet_Contract_UPDATED.sol')

with open(contract, 'r') as f:
    source = f.read()

compiled_contract = compile_source(source)

factory_filepath = os.path.join(os.getcwd(), 'walletFactory')
wallet_filepath = os.path.join(os.getcwd(), 'walletContract')

with open(factory_filepath, 'w') as f:
    json.dump(compiled_contract['<stdin>:WalletFactory'], f)

with open(wallet_filepath, 'w') as w:
    json.dump(compiled_contract['<stdin>:KYC_Wallet'], w)