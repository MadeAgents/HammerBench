import os
import re
import json
import sys
from datetime import datetime
from rouge import Rouge
# from openai import OpenAI
# client = OpenAI(api_key="None", base_url="http://10.237.50.193:8000/v1")

# sys.path.append('/home/notebook/data/en/personal/80397352/HammerBench/data_generation/')
# from LLM_check.prompt import label_prompt, label_prompt_en
def LLM_label_param(query, model_output, label):
    label = dict(sorted(label.items(), key=lambda x:x[0]))
    model_output = dict(sorted(model_output.items(), key=lambda x:x[0]))
    model_input = label_prompt_en.replace("{query}", query).replace("{model_output}", json.dumps(model_output, ensure_ascii=False)).replace("{label}", json.dumps(label, ensure_ascii=False))
    # response = client.chat.completions.create(model="llama3", messages=[{"role": "user", "content": model_input}], stop=["<|end_of_text|>","<|im_end|>"], temperature=0).choices[0].message.content
    return model_input   # 没有服务则返回输入
    if "True" in response:
        return True
    else:
        return False
def LLM_label_param_zh(query, model_output, label):
    label = dict(sorted(label.items(), key=lambda x:x[0]))
    model_output = dict(sorted(model_output.items(), key=lambda x:x[0]))
    model_input = label_prompt.replace("{query}", query).replace("{model_output}", json.dumps(model_output, ensure_ascii=False)).replace("{label}", json.dumps(label, ensure_ascii=False))
    # response = client.chat.completions.create(model="llama3", messages=[{"role": "user", "content": model_input}], stop=["<|end_of_text|>","<|im_end|>"], temperature=0).choices[0].message.content
    return model_input   # 没有服务则返回输入
    if "True" in response:
        return True
    else:
        return False
rouge = Rouge()

def calculate_rouge_l_score_en(reference, hypothesis):
    if hypothesis == '' and reference == '':
        return {'r': 1, 'p': 1, 'f': 1}
    elif hypothesis == '':
        return {'r': 0, 'p': 0, 'f': 0}
    elif reference == '':
        return {'r': 0, 'p': 0, 'f': 0}
    reference = reference.strip('.?! ').lower()#.replace(' ','')
    hypothesis = hypothesis.strip('.?! ').lower()#.replace(' ','')
    try:
        scores = rouge.get_scores(hypothesis, reference)
    except:
        return {'r': 0, 'p': 0, 'f': 0}
    rouge_l_score = scores[0]['rouge-l']
    return rouge_l_score
    
def get_e2e_rougel_en(param_dict0, param_dict):
    if type(param_dict) != dict:
        return False
    param_dict0 = {k: str(v) for k, v in param_dict0.items() if v != ''}
    param_dict = {k: str(v) for k, v in param_dict.items() if v != ''}
    for k, v in param_dict.items():
        if k not in param_dict0:
            return False
    if param_dict0 == param_dict:
        return True
    # elif param_dict0.keys() != param_dict.keys():
    #     return False
    else:
        try:
            del(param_dict0['kwargs'])
            del(param_dict['kwargs'])
        except:pass
        if param_dict0 == param_dict:  # 去掉后再次比较
            return True
        
        argval_scores = []
        for k, v in param_dict0.items():
            if k not in param_dict.keys():
                argval_scores.append(0)
            else:
                argval_scores.append(calculate_rouge_l_score_en(v, param_dict[k])['f'])
        if len(param_dict0)>0 and min(argval_scores) >= 0.7:
            return True
    return False


def calculate_rouge_l_score_chinese(reference, hypothesis):
    if hypothesis == '' and reference == '':
        return {'r': 1, 'p': 1, 'f': 1}
    elif hypothesis == '':
        return {'r': 0, 'p': 0, 'f': 0}
    elif reference == '':
        return {'r': 0, 'p': 0, 'f': 0}
    reference = re.sub(r'([\u4e00-\u9fff])', r' \1 ', reference.strip('。！ '))
    hypothesis = re.sub(r'([\u4e00-\u9fff])', r' \1 ', hypothesis.strip('。！ '))
    try:
        scores = rouge.get_scores(hypothesis, reference)
    except:
        return {'r': 0, 'p': 0, 'f': 0}
    rouge_l_score = scores[0]['rouge-l']
    return rouge_l_score
def get_e2e_rougel(param_dict0, param_dict):
    if type(param_dict) != dict:
        return False
    param_dict0 = {k: str(v) for k, v in param_dict0.items() if v != ''}
    param_dict = {k: str(v) for k, v in param_dict.items() if v != ''}
    for k, v in param_dict.items():
        if k not in param_dict0:
            return False
    if param_dict0 == param_dict:
        return True
    # elif param_dict0.keys() != param_dict.keys():
    #     return False
    else:
        try:
            del(param_dict0['kwargs'])
            del(param_dict['kwargs'])
        except:pass
        if param_dict0 == param_dict:  # 去掉后再次比较
            return True
        
        argval_scores = []
        for k, v in param_dict0.items():
            if k not in param_dict.keys():
                argval_scores.append(0)
            else:
                argval_scores.append(calculate_rouge_l_score_chinese(v, param_dict[k])['f'])
        if len(param_dict0)>0 and min(argval_scores) >= 0.7:
            return True
    return False

def get_miss_redundant_num(param_dict0, param_dict):
    # 返回参数幻觉数量、参数缺失数量
    key0 = param_dict0.keys()
    key = param_dict.keys()
    return len(key-key0), len(key0-key)