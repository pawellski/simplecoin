from requests import get, post

NODES_IPS = ['http://localhost:8081', 'http://localhost:8082', 'http://localhost:8083', 'http://localhost:8084']
MINER_REWARD = 0.005

# Turn off generators
for ip in NODES_IPS:
    post(f'{ip}/stop-generator')

# Get balances
balances = []
for idx, ip in enumerate(NODES_IPS):
    balances.append(get(f'{ip}/current-balance').json()['current_balance'])
    print(f'Node{idx} balance: {balances[idx]}')

block_count = get(f'{NODES_IPS[0]}/get-block-count').json()['count'] - 1  # Minus genesis block (no reward)
print(f'Mined block count: {block_count}')

total_reward = block_count * MINER_REWARD
total_balance = sum(balances)

print('Total start amount: 400 (100 per each block)')
print(f'Total balance (sum of balances): {total_balance}')
print(f'Total reward for mining {block_count} blocks: {total_reward}')
print(f'(Total balance - Total reward): {round(total_balance - total_reward, 3)}')