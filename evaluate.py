# According to the results of reasoning, metrics are calculated and evaluated.
import json
import sys, os
from evaluation.process_output import parse_response, parse_mistral, parse_xlam, parse_toolace   # Post-processing here
from evaluation.metrics import get_e2e_rougel, get_e2e_rougel_en, get_miss_redundant_num

log_dir = sys.argv[1]
language = sys.argv[2]
inference_res = json.load(open(log_dir,'r'))

json_format_error = 0
tool_rej_rate = 0
Func_Acc = []
Args_Acc = []
hallucination_num, miss_num = [], []

for i in range(len(inference_res)):
    try:
        if 'ministral' in log_dir.lower():
            api_name, param_dict = parse_mistral(inference_res[i]['predict'])[0]
        elif 'xlam' in log_dir.lower():
            api_name, param_dict = parse_xlam(inference_res[i]['predict'])[0]
        elif 'toolace' in log_dir.lower():
            api_name, param_dict = parse_toolace(inference_res[i]['predict'])[0]
        else:
            api_name, param_dict = parse_response(inference_res[i]['predict'], '```json', '```')[0]
        inference_res[i]['predict'] = {'name':api_name ,'arguments':param_dict}
    except:pass
    
    if type(inference_res[i]['predict'])!=str and inference_res[i]['predict']['name']==inference_res[i]['label']['name']:
        Func_Acc.append(True)
    else:
        tool_rej_rate += 'sorry' in str(inference_res[i]['predict']).lower()
        Func_Acc.append(False)

    if type(inference_res[i]['predict'])!=str:
        if language=='en':
            turn_flag = get_e2e_rougel_en(inference_res[i]['label']['arguments'], inference_res[i]['predict']['arguments'])
            hallucination0, miss0 = get_miss_redundant_num(inference_res[i]['label']['arguments'], inference_res[i]['predict']['arguments'])
            hallucination_num.append(hallucination0)
            miss_num.append(miss0)
        else:
            turn_flag = get_e2e_rougel(x['label']['arguments'], x['predict']['arguments'])
            hallucination0, miss0 = get_miss_redundant_num(x['label']['arguments'], x['predict']['arguments'])
            hallucination_num.append(hallucination0)
            miss_num.append(miss0)
    else:  # 0 parameters are predicted, but recall still has a denominator
        turn_flag = False
        hallucination_num.append(0)
        num0 = len(x['label']['arguments'])
        miss_num.append(num0)
        json_format_error += 1
        # print(x['predict'])
    
    Args_Acc.append(turn_flag)
    
# print(snap_shot_id)
print("Rejection rate：", tool_rej_rate/len(inference_res))
print("Output string ratio：", json_format_error/len(Func_Acc))
print("Average number of parameter hallucinations：", sum(hallucination_num)/(len(hallucination_num)+1e-9) )
print("Average number of missing parameters：", sum(miss_num)/(len(miss_num)+1e-9))
print("Func_Acc：", sum(Func_Acc)/len(Func_Acc))
# Eliminate Func Acc errors
print(len(Func_Acc), len(hallucination_num))
for i in range(len(Func_Acc)-1,-1,-1):
    if not Func_Acc[i]:
        delete = hallucination_num.pop(i)
        delete = miss_num.pop(i)
    else:
        hallucination_num[i] = hallucination_num[i]>0
        miss_num[i] = miss_num[i]>0

print(len(Func_Acc), len(hallucination_num))
print("PN_FP：", sum(hallucination_num)/(len(hallucination_num)+1e-9))
print("PN_FN：", sum(miss_num)/(len(miss_num)+1e-9))
print("Args_Acc：", sum(Args_Acc)/len(Args_Acc))