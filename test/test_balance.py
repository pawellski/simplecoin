from requests import get, post
import sys

NODES_IPS = ['http://localhost:8081', 'http://localhost:8082', 'http://localhost:8083', 'http://localhost:8084']
MINER_REWARD = 0.005

id = sys.argv[1]

# Turn off generators
#for ip in NODES_IPS:
#    post(f'{ip}/stop-generator')
#    post(f'{ip}/stop-miner')

# Get balances
balances = []
for idx in range(1,5):
    balances.append(get(f'http://localhost:808{id}/current-balance/{idx}').json()['current_balance'])
    print(f'Node{idx} balance: {balances[idx-1]}')

block_count = get(f'http://localhost:808{id}/get-block-count').json()['count'] - 1  # Minus genesis block (no reward)
print(f'Mined block count: {block_count}')

total_reward = block_count * MINER_REWARD
total_balance = sum(balances)

print('Total start amount: 400 (100 per each block)')
print(f'Total balance (sum of balances): {total_balance}')
print(f'Total reward for mining {block_count} blocks: {total_reward}')
print(f'(Total balance - Total reward): {round(total_balance - total_reward, 3)}')