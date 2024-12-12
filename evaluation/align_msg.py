import json, sys
log_dir = sys.argv[1]  # 'logs/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4/'
MT_0 = json.load(open(log_dir+'HammerBench_Based/MT_0.json','r'))
MT_res = json.load(open(log_dir+'HammerBench_Based/MT_res.json','r'))
LLM_check_L = json.load(open(log_dir+'HammerBench_Based/LLM_check_L.json','r'))
LLM_check_response = json.load(open(log_dir+'HammerBench_Based/LLM_check_response.json','r'))
turn_flags_res = json.load(open(log_dir+'HammerBench_Based/turn_flags_res.json','r'))

test_type = sys.argv[2]  # 'xQxA'
MT_id = json.load(open(f'data/en/multi-turn/{test_type}.json','r'))
MT_id = [x['id'] for x in MT_id]

# 按照 id提取出相应数据和结果
new_0, new_res = [], []
new_L, new_response, new_turn_flags_res = [], [], []
for i in MT_id:
    new_0.append(MT_0[i])
    new_res.append(MT_res[i])
    new_L.append(LLM_check_L[i])
    new_response.append(LLM_check_response[i])
    new_turn_flags_res.append(turn_flags_res[i])
import os
if not os.path.exists(log_dir+test_type+'/MT0'):
    os.mkdir(log_dir+test_type+'/MT0')
with open(log_dir+test_type+'/MT0/MT_0.json', 'w') as fp:
    json.dump(new_0 ,fp ,indent=2, ensure_ascii=False)
    
with open(log_dir+test_type+'/MT0/MT_res.json', 'w') as fp:
    json.dump(new_res ,fp ,indent=2, ensure_ascii=False)

with open(log_dir+test_type+'/MT0/LLM_check_L.json', 'w') as fp:
    json.dump(new_L ,fp ,indent=2, ensure_ascii=False)

with open(log_dir+test_type+'/MT0/LLM_check_response.json', 'w') as fp:
    json.dump(new_response ,fp ,indent=2, ensure_ascii=False)

with open(log_dir+test_type+'/MT0/turn_flags_res.json', 'w') as fp:
    json.dump(new_turn_flags_res,fp ,indent=2, ensure_ascii=False)