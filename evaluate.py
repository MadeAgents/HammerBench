# According to the results of reasoning, metrics are calculated and evaluated.
import json
import sys, os
from evaluation.process_output import parse_response, parse_mistral, parse_xlam, parse_toolace   # Post-processing here
from evaluation.metrics import get_e2e_rougel, get_e2e_rougel_en, get_miss_redundant_num
from evaluation.prompt_judge import LLM_label_param_zh, LLM_label_param

from evaluation.llm_judge import LLM_eval, calculate_turn, FN_PN

is_llm_judge = False

df = []
log_dir = sys.argv[1]
language = sys.argv[2]
flag_eval = sys.argv[3] # 'all'  '-1'  'mid' '0'
print(flag_eval)
MT = json.load(open(log_dir+'MT_0.json','r'))
MT_res = json.load(open(log_dir+'MT_res.json','r'))


json_format_error = 0
tool_rej_rate = 0
Func_Acc = 0
Args_Acc = []
PRs = []
success_rate = []
hallucination_num, miss_num = [], []
llm_inputs, llm_inputs_L = [], []

if 'SO_case1' in log_dir:
    snapid_dir = '../data/en/multi-turn/snapshot_id/snap_shot_id_SO_case1.json'
elif 'SO_case2' in log_dir:
    snapid_dir = '../data/en/multi-turn/snapshot_id/snap_shot_id_SO_case2.json'
elif 'External' in log_dir:
    snapid_dir = '../data/en/multi-turn/snapshot_id/snap_shot_id_External.json'
else:snapid_dir = None

if flag_eval!='mid':snapid_dir = None

if snapid_dir:
    snap_shot_id = json.load(open(snapid_dir, 'r'))
    if 'SO_case2' in log_dir and 'MT0' not in log_dir:
        snap_shot_id = [L*2 for L in snap_shot_id]   # When a new turn is inserted
        for x in snap_shot_id:x[1]+=1
else:
    snap_shot_id = []   # Define the id of the slice, [[0,1],[-1]...], which can be imported from file

for i in range(len(MT_res)):
    n_turn = len(MT_res[i]['FC_res'])
    # post-processing
    for j in range(n_turn):
        try:
            if 'ministral' in log_dir.lower():
                api_name, param_dict = parse_mistral(MT_res[i]['FC_res'][j]['predict'])[0]
            elif 'xlam' in log_dir.lower():
                api_name, param_dict = parse_xlam(MT_res[i]['FC_res'][j]['predict'])[0]
            elif 'toolace' in log_dir.lower():
                api_name, param_dict = parse_toolace(MT_res[i]['FC_res'][j]['predict'])[0]
            else:
                api_name, param_dict = parse_response(MT_res[i]['FC_res'][j]['predict'], '```json', '```')[0]
            MT_res[i]['FC_res'][j]['predict'] = {'name':api_name ,'arguments':param_dict}
        except:pass
    
    df0 = {}
    df0['conversation'] = json.dumps(MT[i]['messages'], indent=2, ensure_ascii=False)
    df0['FC_res'] = json.dumps(MT_res[i]['FC_res'], indent=2, ensure_ascii=False)
    toolname = MT[i]['messages'][1]['content']['name']
    if type(MT_res[i]['FC_res'][0]['predict'])!=str and MT_res[i]['FC_res'][0]['predict']['name']==MT_res[i]['FC_res'][0]['label']['name']:
        Func_Acc += 1
        df0['Func Name'] = True
    else:
        tool_rej_rate += 'sorry' in str(MT_res[i]['FC_res'][0]['predict']).lower()
        df0['Func Name'] = False
    # Evaluate the Args
    if not snapid_dir or flag_eval!='mid':
        snap_shot_id0 = []

    turn_flags, llm_inputs0 = [], []
    hallucination_num0, miss_num0 = [], []
    for j in range(n_turn):
        # Only the last snapshot is evaluated
        if j==n_turn-1 and flag_eval=='-1':  #  and not snapid_dir
            snap_shot_id0.append(j)
        elif j==0 and flag_eval=='0':
            snap_shot_id0.append(j)
        elif flag_eval=='all':
            snap_shot_id0.append(j)

        x = MT_res[i]['FC_res'][j]
        # input、predict、label
        turn_flag = x['label']==x['predict']
        if type(x['predict'])!=str:
            if language=='en':
                turn_flag = get_e2e_rougel_en(x['label']['arguments'], x['predict']['arguments'])
                try:flag_llm = LLM_label_param(x['input'].replace('\n','  '), x['predict']['arguments'], x['label']['arguments'])
                except:flag_llm = ''
                llm_inputs0.append(flag_llm)
                hallucination0, miss0 = get_miss_redundant_num(x['label']['arguments'], x['predict']['arguments'])
                hallucination_num0.append(hallucination0)
                miss_num0.append(miss0)
            else:
                turn_flag = get_e2e_rougel(x['label']['arguments'], x['predict']['arguments'])
                try:flag_llm = LLM_label_param_zh(x['input'].replace('\n','  '), x['predict']['arguments'], x['label']['arguments'])
                except:flag_llm = ''
                llm_inputs0.append(flag_llm)
                # llm_inputs0.append(x['predict'])
                hallucination0, miss0 = get_miss_redundant_num(x['label']['arguments'], x['predict']['arguments'])
                hallucination_num0.append(hallucination0)
                miss_num0.append(miss0)
        else:  # 0 parameters are predicted, but recall still has a denominator
            hallucination_num0.append(0)
            num0 = len(x['label']['arguments'])
            miss_num0.append(num0)
            json_format_error += 1
            # print(x['predict'])
            llm_inputs0.append("please output False.")
        
        turn_flags.append(turn_flag)
    # Record the slices that need to be evaluated each time
    if not snapid_dir:
        snap_shot_id.append(snap_shot_id0)
    hallucination_num.append([hallucination_num0[k] for k in snap_shot_id[i]])
    miss_num.append([miss_num0[k] for k in snap_shot_id[i]])

    llm_inputs += llm_inputs0
    llm_inputs_L.append(len(llm_inputs))
    df0['Args'] = turn_flags
    df.append(df0)
    idx, PR, success_rate0, Args_Acc0 = calculate_turn([turn_flags[k] for k in snap_shot_id[i]], df0['Func Name'])
    Args_Acc.append((Args_Acc0, len(snap_shot_id[i])))
    
    success_rate.append(success_rate0)
    PRs.append(PR)
    if not success_rate[-1]:
        # print(turn_flags, MT_res[i])
        pass

# print(snap_shot_id)
print("Rejection rate：", tool_rej_rate/len(MT_res))
print("Output string ratio：", json_format_error/len(llm_inputs_L))
print("Output string ratio：", json_format_error/sum(llm_inputs_L))
print("Average number of parameter hallucinations：", sum([sum(x) for x in hallucination_num])/(sum([len(x) for x in hallucination_num])+1e-9))
print("Average number of missing parameters：", sum([sum(x) for x in miss_num])/(sum([len(x) for x in miss_num])+1e-9))
# Eliminate Func Acc errors
print(len(df), len(hallucination_num))
for i in range(len(df)-1,-1,-1):
    if not df[i]['Func Name']:
        delete = hallucination_num.pop(i)
        delete = miss_num.pop(i)
    else:
        for j in range(len(hallucination_num[i])):
            hallucination_num[i][j] = hallucination_num[i][j]>0
        for j in range(len(miss_num[i])):
            miss_num[i][j] = miss_num[i][j]>0
print(len(df), len(hallucination_num))
print("PN_FP：", sum([sum(x) for x in hallucination_num])/(sum([len(x) for x in hallucination_num])+1e-9))
print("PN_FN：", sum([sum(x) for x in miss_num])/(sum([len(x) for x in miss_num])+1e-9))
print("Func_Acc：", Func_Acc/len(MT))
print("Args_Acc：", sum([x[0] for x in Args_Acc])/sum([x[1] for x in Args_Acc]))
print("PR：", sum(PRs)/(len(PRs)+1e-9))
print("SR：", sum(success_rate)/(len(success_rate)+1e-9))

import pandas as pd
df = pd.DataFrame(df)
df.to_csv(log_dir+'badcase.csv', index=0)

if not os.path.exists(log_dir+'turn_flags_res.json') and is_llm_judge:#language=='en':
    LLM_eval(llm_inputs, llm_inputs_L, snap_shot_id, df, log_dir, language)
elif is_llm_judge:
    turn_flags_res = json.load(open(log_dir+'turn_flags_res.json', 'r'))
    llm_inputs_L = json.load(open(log_dir+'LLM_check_L.json', 'r'))
    turn_completion_rates, success_rate, Args_Acc = [], [], []
    for i in range(len(turn_flags_res)):
        turn_flags = [turn_flags_res[i][k] for k in snap_shot_id[i]]
        FC_res0 = json.loads(df.loc[i,'FC_res'])
        FC_res0 = [FC_res0[k] for k in snap_shot_id[i]]
        turn_flags = FN_PN(FC_res0, turn_flags)
        idx, turn_completion_rate, success_rate0, Args_Acc0 = calculate_turn(turn_flags, df.loc[i,'Func Name'])
        Args_Acc.append((Args_Acc0, len(snap_shot_id[i])))
        turn_completion_rates.append(turn_completion_rate)
        success_rate.append(success_rate0)
    print("Args_Acc LLM：", sum([x[0] for x in Args_Acc])/sum([x[1] for x in Args_Acc]))
    print("PR LLM：", sum(turn_completion_rates)/(len(turn_completion_rates)+1e-9))
    print("SR LLM：", sum(success_rate)/(len(success_rate)+1e-9))