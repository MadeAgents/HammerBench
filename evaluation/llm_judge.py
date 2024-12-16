
import json
def calculate_turn(turn_flags, funcAcc):
    try:
        idx = turn_flags.index(False)
        PR = idx/len(turn_flags)
    except:  # When all are True
        idx = -1
        PR = 1
    if not funcAcc:
        PR=0
        success_rate0 = False
    else:
        success_rate0 = sum(turn_flags)==len(turn_flags) and turn_flags!=[]
    return idx, PR, success_rate0, sum(turn_flags)*int(funcAcc)
def FN_PN(FC_res0, turn_flags0):
    res, i = [], 0
    for x in FC_res0:
        if isinstance(x['predict'], str):
            res.append(False)
        else:
            FN_PN = x['predict']['name'] == x['label']['name'] and x['predict']['arguments'].keys() == x['label']['arguments'].keys()
            res.append(FN_PN and turn_flags0[i])
        i += 1
    return res

def LLM_eval(llm_inputs, llm_inputs_L, snap_shot_id, df, log_dir, language='en'):
    from vllm import LLM, SamplingParams
    sampling_params = SamplingParams(temperature=0.0, max_tokens=20)
    if language=='en':
        model_path="hugging-quants/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4"
    elif language=='zh':
        model_path="Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4"
    try:llm = LLM(model=model_path, tensor_parallel_size=1, max_model_len=6400, gpu_memory_utilization=0.88, dtype="bfloat16")  # , max_num_seqs=8
    except:llm = LLM(model=model_path, tensor_parallel_size=1, max_model_len=6400, gpu_memory_utilization=0.88, dtype="float32")
    tokenizer = llm.get_tokenizer()
    tokenizer.padding_side = 'left'
    turn_completion_rates, success_rate, Args_Acc = [], [], []
    print(llm_inputs[0])
    outputs = llm.generate(llm_inputs, sampling_params, use_tqdm=True)
    response = [output.outputs[0].text for output in outputs]
    print(response[0])
    llm_inputs_L = [0]+llm_inputs_L
    turn_flags_res = []
    for i in range(len(llm_inputs_L)-1):        
        turn_flags = []
        for flag_llm in response[llm_inputs_L[i]: llm_inputs_L[i+1]]:
            turn_flags.append("True" in flag_llm)
        # 
        FC_res0 = json.loads(df.loc[i,'FC_res'])
        FC_res0 = [FC_res0[k] for k in snap_shot_id[i]]
        turn_flags = FN_PN(FC_res0, turn_flags)
        turn_flags_res.append(turn_flags)
        idx, turn_completion_rate, success_rate0, Args_Acc0 = calculate_turn([turn_flags[k] for k in snap_shot_id[i]], df.loc[i,'Func Name'])
        Args_Acc.append((Args_Acc0, len(snap_shot_id[i])))
        turn_completion_rates.append(turn_completion_rate)
        success_rate.append(success_rate0)

    print("Args_Acc LLM：", sum([x[0] for x in Args_Acc])/sum([x[1] for x in Args_Acc]))
    print("PR LLM：", sum(turn_completion_rates)/(len(turn_completion_rates)+1e-9))
    print("SR LLM：", sum(success_rate)/(len(success_rate)+1e-9))
    with open(log_dir+'LLM_check_response.json', 'w') as fp:
        json.dump(response, fp ,indent=2, ensure_ascii=False)
    with open(log_dir+'LLM_check_L.json', 'w') as fp:
        json.dump(llm_inputs_L, fp ,indent=2, ensure_ascii=False)
    with open(log_dir+'turn_flags_res.json', 'w') as fp:
        json.dump(turn_flags_res, fp ,indent=2, ensure_ascii=False)