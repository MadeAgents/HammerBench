# pip install sentence-transformers openpyxl faiss-gpu langchain==0.1.0 case-convert modelscope -i http://mirrors.oppo.local/pypi --trusted-host mirrors.oppo.local
# 需要将数据处理成 shareGPT 的格式
# 每一个step都判定一下，FC以及相应 提问的能力，相关的提问用 72B模型或者 embedding模型判定。
import sys, os, json
import random
random.seed(42)
from template import llama_model_input, qwen25_model_input, mistral_model_input, xlam_model_input, ToolACE_model_input, hammer_model_input
from vllm import LLM, SamplingParams
sampling_params = SamplingParams(temperature=0.0, max_tokens=4096)

data_path = sys.argv[1]  # 用哪个类型数据 zh/MT_random_merge.json
print(data_path)
language_tag = sys.argv[3]  #   'en'
model_path = sys.argv[2]  #

try:llm = LLM(model=model_path, tensor_parallel_size=1, max_model_len=4096, gpu_memory_utilization=0.8, dtype="bfloat16")
except:llm = LLM(model=model_path, tensor_parallel_size=1, max_model_len=4096, gpu_memory_utilization=0.8, dtype="float32")
tokenizer = llm.get_tokenizer()
tokenizer.padding_side = 'left'


def our2openai(param):
    res={}
    for x in param:
        res[x["name"]] = {"type":x["type"] ,"description":x["description"]}
    return {"type": "object", "properties":res, "required": list(res.keys())}
def get_input(query, tools=None):  # prompt在此处定义
    if tools:
        if 'llama' in model_path.lower():
            model_input, label = llama_model_input(query, tools, 'null' )
        elif 'qwen' in model_path.lower():
            model_input, label = qwen25_model_input(query, tools, 'null' )
        elif 'ministral' in model_path.lower():
            model_input, label = mistral_model_input(query, tools, 'null' )
        elif 'xlam' in model_path.lower():
            model_input, label = xlam_model_input(query, tools, 'null' )
        elif 'toolace' in model_path.lower():
            model_input, label = ToolACE_model_input(query, tools, 'null' )
        elif 'hammer' in model_path.lower():
            model_input, label = hammer_model_input(query, tools, 'null' )
        else:
            model_input, label = llama_model_input(query, tools, 'null' )
    else:
        if 'llama' in model_path.lower():
            model_input = "<|begin_of_text|><|start_header_id|>system\nYou are a helpful assistant.<|end_header_id|>\n\n<|start_header_id|>user<|end_header_id|>\n\n"+query+"<|start_header_id|>assistant<|end_header_id|>\n"
        elif 'qwen' in model_path.lower():
            model_input = '<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n' + query +'<|im_end|>\n<|im_start|>assistant\n'
    
    return model_input

MT = json.load(open(data_path, 'r'))   # user、function call、assistant交替

import tqdm
model_inputs, sep_n = [], []
for i in tqdm.tqdm(range(0, len(MT))):
    recall_tools = MT[i]['multiple_tools']
    try:single_tool = MT[i]['single_tool']
    except:pass
    # toolname = MT[i]['messages'][1]['content']['name']
    # tool_info = single_tool[0]
    
    history, n_turn = [], len(MT[i]['messages'])
    user_n = 0
    for j in range(n_turn):
        x = MT[i]['messages'][j]
        if x['role']=='user':  # user的地方都默认进行 function calling能力评估
            # history = history[-2:]   # 历史信息只取function call体现
            history.append('user:'+x['content'])
            query = '\n'.join(history)
            if j==0:
                model_input = get_input(query, recall_tools )
            else:
                model_input = get_input(query, single_tool )
            user_n += 1
            model_inputs.append((query,model_input))
        elif x['role']=='assistant':
            history.append('assistant:'+x['content'] )
        # elif x['role']=='function call':  #  是否引入
        #     history.append('previous: ```json\n'+json.dumps(x['content'], ensure_ascii=False)+'\n```' )
    sep_n.append(user_n)

queries = [x[0] for x in model_inputs]
model_inputs = [x[1] for x in model_inputs]
outputs = llm.generate(model_inputs, sampling_params, use_tqdm=True)
response = [output.outputs[0].text for output in outputs]

print("对齐检查", sum(sep_n)==len(model_inputs))
import numpy as np
res = []
sep_n = np.cumsum([0]+sep_n)
for i in range(len(sep_n)-1):
    FC0, j = [], 0
    for out, query in zip(response[sep_n[i]:sep_n[i+1]], queries[sep_n[i]:sep_n[i+1]]):
        FC0.append({'input':query, 'predict':out, 'label':MT[i]['messages'][1+3*j]['content']})
        j += 1
    res.append({'FC_res':FC0})

data_type = os.path.split(data_path)[1][:-5]
save_dir = f'logs/{language_tag}/'+os.path.split(model_path)[1]
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
save_dir += f'/{data_type}/'
if not os.path.exists(save_dir):
    os.mkdir(save_dir)
with open(save_dir+'MT_0.json', 'w') as fp:
    json.dump(MT, fp, indent=2, ensure_ascii=False)
with open(save_dir+'MT_res.json', 'w') as fp:
    json.dump(res, fp, indent=2, ensure_ascii=False)