import json, re, sys
log_file = sys.argv[1]  #  'task.txt'
with open(log_file, 'r') as fp:
    all_logs = fp.readlines()

all_texts = '\n'.join(all_logs)

Func_Accs = re.findall('Func_Acc：(.*?)\n', all_texts)
PR = re.findall('PR：(.*?)\n', all_texts)
SR = re.findall('PR：(.*?)\n', all_texts)
PN_FP = re.findall('PN_FP：(.*?)\n', all_texts)
PN_FN = re.findall('PN_FN：(.*?)\n', all_texts)

if 1:#'llama' in log_file:
    Args_Accs = re.findall('Args_Acc LLM：(.*?)\n', all_texts)
    llmPR = re.findall('PR LLM：(.*?)\n', all_texts)
    llmsuccess_rate = re.findall('SR LLM：(.*?)\n', all_texts)
else:
    llmPR = [1]*len(Func_Accs)
    llmsuccess_rate = [1]*len(Func_Accs)
import pandas as pd
df = pd.DataFrame()
# print(Func_Accs, PR, SR, llmPR, llmsuccess_rate)
for df0 in [Func_Accs, PN_FP, PN_FN, Args_Accs, llmPR, llmsuccess_rate, PR, SR]:
    df = pd.concat((df, pd.DataFrame(df0) ), axis=1)
print(df.shape)
df.columns = ["Func_Accs", "PN_FP", "PN_FN", "Args_Accs LLM","llmPR", "llmsuccess_rate", "PR", "SR", "precisions", "recalls", "f1s"]
df.to_csv(log_file.replace(".log",".csv"), index=0)
print(len(Func_Accs), len(PR), len(SR), len(precisions), len(recalls), len(f1s), len(llmPR), len(llmsuccess_rate))
print(len(Func_Accs)==len(PR)==len(SR)==len(precisions)==len(recalls)==len(f1s)==len(llmPR)==len(llmsuccess_rate))