import asyncio
from sys import platform

from custom_types import FormattedAccount
from .append_file import append_file
from utils import loader

if platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def format_result(account_data: FormattedAccount,
                        total_usd_balance: float,
                        token_balances: dict,
                        pools_balances: dict,
                        nfts_count: int,
                        args) -> bool:
    tokens_balance: float = 0
    pools_balance: float = 0
    split: int = int(args.split)
    account_data_dict: dict = {
        'address': account_data.address,
        'private_key': account_data.private_key,
        'mnemonic': account_data.mnemonic
    }
    account_data_for_file: str = ' | '.join([current_value for current_value
                                             in account_data_dict.values()
                                             if current_value])

    for current_pool_chain in list(pools_balances.keys()):
        for current_pool_name in list(pools_balances[current_pool_chain].keys()):
            for current_pool_token_data in pools_balances[current_pool_chain][current_pool_name]:
                if current_pool_token_data.get('amount') and current_pool_token_data.get('price'):
                    current_pool_balance: float = (current_pool_token_data['amount'] * current_pool_token_data['price'])
                    pools_balance += current_pool_balance

    for current_token_chain in list(token_balances.keys()):
        for current_token_data in token_balances[current_token_chain]:
            if current_token_data.get('amount') and current_token_data.get('price'):
                current_token_balance: float = (current_token_data['amount'] * current_token_data['price'])
                tokens_balance += current_token_balance

    tokens_balance: float = round(number=tokens_balance,
                                  ndigits=2)
    pools_balance: float = round(number=pools_balance,
                                 ndigits=2)
    total_usd_balance: float = round(number=total_usd_balance,
                                     ndigits=2)

    async with asyncio.Lock():
        await append_file(
            file_path='results/with_nft.txt',
            file_content=f'{account_data_for_file} | {nfts_count} NFT\'s\n'
        )
    if split == 0:
        file_path = 'results/all_balances.txt'
    elif split == 1:
        if total_usd_balance <= 0:
            async with asyncio.Lock():
                await append_file(
                    file_path='results/zero_balance.txt',
                    # file_content=f'{account_data_for_file} | Total Balance: ${total_usd_balance} | '
                    #              f'Tokens Balance: ${tokens_balance} | Pools Balance: ${pools_balance}\n'
                    file_content=f'{account_data_for_file}\t{total_usd_balance}\n'
                )

            return True
        elif total_usd_balance < 1:
            file_path = 'results/0_1_balances.txt'
        elif total_usd_balance < 100:
            file_path = 'results/1_100_balances.txt'
        elif total_usd_balance < 500:
            file_path = 'results/100_500_balances.txt'
        elif total_usd_balance < 1000:
            file_path = 'results/500_1000_balances.txt'
        else:
            file_path = 'results/1000_plus_balances.txt'

    async with asyncio.Lock():
        await append_file(
            file_path=file_path,
            # file_content=f'{account_data_for_file} | Total Balance: ${total_usd_balance} | '
            #              f'Tokens Balance: ${tokens_balance} | Pools Balance: ${pools_balance}\n'
            file_content=f'{account_data_for_file} \t{total_usd_balance}\n'
        )

    return True
