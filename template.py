import json

QA_mode=False
format_desc = '''\nAttention! For time parameters, please fill in the format as described in the user request, and do not automatically convert the format! For example:\nuser: Set an alarm for 8 a.m. tomorrow\nassistant：{"name":"UtilityTools.AlarmClock.addAlarm", "arguments":{"time":"8 a.m. tomorrow"}}\n
\n## Note! Please do not hallucinate parameters. If some parameters are not mentioned in the user request, please directly output an empty string '' For example:\nuser:Check my traffic violation record to see what happened. \nassistant:```json\n{"name": "Navigation.TrafficViolations.viewViolationDetail", "arguments":{"plate_number": "","city": "","time": ""}}\n```.\nNever ask to the user for missing parameters!Output tool call!\n'''

# llama模型输入
system_llama32 = '''You have access to the following functions.\n{tools_desc}\n To call a function, please respond with JSON for a function call.Respond in the format ```json{"name": function name, "parameters": dictionary of argument name and its value}. ```'''
def llama_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_llama32.replace('{tools_desc}', '\n'.join([json.dumps(t, indent=4, ensure_ascii=False) for t in tools]) )
    system_content +=f'{format_desc}## If all the above tools are not suitable, you must output: Sorry, no tool is suitable for your request.\n\nLet\'s start!'
    sys_prefix, user_prefix = '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n', '<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n'
    user_suffix = '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n'
    
    return sys_prefix + system_content + user_prefix + query + user_suffix, output

# Mistral模型输入
system_mistral = '''<s>[AVAILABLE_TOOLS]\n{tools_desc}\n[/AVAILABLE_TOOLS][INST]'''
def mistral_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_mistral.replace('{tools_desc}', json.dumps([{"type": "function", "function":t} for t in tools], ensure_ascii=False) )
    format_desc = '''\nAttention! For time parameters, please fill in the format as described in the user request, and do not automatically convert the format! For example:\nuser: Set an alarm for 8 a.m. tomorrow\nassistant：[{"name":"UtilityTools.AlarmClock.addAlarm", "arguments":{"time":"8 a.m. tomorrow"}}]\n
\n## Note! Please do not hallucinate parameters. If some parameters are not mentioned in the user request, please directly output an empty string '' For example:\nuser:Check my traffic violation record to see what happened. \nassistant:[{"name": "Navigation.TrafficViolations.viewViolationDetail", "arguments":{"plate_number": "","city": "","time": ""}}].\nNever ask to the user for missing parameters!Output tool call!\n'''
    system_content +=f'{format_desc}## If all the above tools are not suitable, you must output: Sorry, no tool is suitable for your request.\n\nLet\'s start!'
    sys_prefix, user_prefix = '', '\n\n'
    user_suffix = '[/INST]'
    
    return sys_prefix + system_content + user_prefix + query + user_suffix, output

# ToolACE模型输入
system_ToolACE = '''You are an expert in composing functions. You are given a question and a set of possible functions. Based on the question, you will need to make one or more function/tool calls to achieve the purpose.
If none of the function can be used, point it out. If the given question lacks the parameters required by the function, also point it out.
You should only return the function call in tools call sections.

If you decide to invoke any of the function(s), you MUST put it in the format of [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]
You SHOULD NOT include any other text in the response.
Here is a list of functions in JSON format that you can invoke.\n{tools_desc}\n'''
def ToolACE_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_ToolACE.replace('{tools_desc}', json.dumps(tools, ensure_ascii=False) )
    format_desc = '''\nAttention! For time parameters, please fill in the format as described in the user request, and do not automatically convert the format! For example:\nuser: Set an alarm for 8 a.m. tomorrow\nassistant：[UtilityTools.AlarmClock.addAlarm(time="8 a.m. tomorrow")]\n
\n## Note! Please do not hallucinate parameters. If some parameters are not mentioned in the user request, please directly output an empty string '' For example:\nuser:Check my traffic violation record to see what happened. \nassistant:[Navigation.TrafficViolations.viewViolationDetail(plate_number="",city="",time="")].\nNever ask to the user for missing parameters!Output tool call!\n'''
    system_content +=f'{format_desc}## If all the above tools are not suitable, you must output: None of the functions can be used to address the question.\n\nLet\'s start!'
    sys_prefix, user_prefix = '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n', '<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n'
    user_suffix = '<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n'
    
    return sys_prefix + system_content + user_prefix + query + user_suffix, output

# xlam模型输入
system_xlam = '''You are an AI assistant for function calling.For politically sensitive questions, security and privacy issues, and other non-computer science questions, you will refuse to answer
### Instruction:\n[BEGIN OF TASK INSTRUCTION]\n{task_instruction}\n[END OF TASK INSTRUCTION]\n\n[BEGIN OF AVAILABLE TOOLS]\n{tools_desc}\n[END OF AVAILABLE TOOLS]\n
[BEGIN OF FORMAT INSTRUCTION]\n{format_instruction}\n[END OF FORMAT INSTRUCTION]\n\n[BEGIN OF QUERY]\n{query}\n[END OF QUERY]\n\n### Response:'''
def xlam_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_xlam.replace('{task_instruction}', '' )
    system_content = system_content.replace('{tools_desc}', json.dumps(tools, ensure_ascii=False) )
    format_desc = '''\nAttention! For time parameters, please fill in the format as described in the user request, and do not automatically convert the format! For example:\nuser: Set an alarm for 8 a.m. tomorrow\nassistant：{"tool_calls":[{"name":"UtilityTools.AlarmClock.addAlarm", "arguments":{"time":"8 a.m. tomorrow"}}]}\n
\n## Note! Please do not hallucinate parameters. If some parameters are not mentioned in the user request, please directly output an empty string '' For example:\nuser:Check my traffic violation record to see what happened. \nassistant:{"tool_calls":[{"name": "Navigation.TrafficViolations.viewViolationDetail", "arguments":{"plate_number": "","city": "","time": ""}}]}.\nNever ask to the user for missing parameters!Output tool call!\n
Let\'s start!'''
    format_desc = '''The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
The example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please make tool_calls an empty list '[]'.
```
{
    "tool_calls": [
    {"name": "func_name1", "arguments": {"argument1": "value1", "argument2": "value2"}},
    ... (more tool calls as required)
    ]
}
```''' + format_desc
    system_content = system_content.replace('{format_instruction}', format_desc)
    
    return system_content.replace('{query}', query), output

# Qwen模型输入
system_72B = '''You are Qwen, created by Alibaba Cloud. You are a helpful assistant.\n\n# Tools\n\nYou may call one or more functions to assist with the user query.\n\nYou are provided with function signatures within :\n<tools>
{tools_desc}
\n</tools>\n\nFor each function call, return a json object with function name and arguments within :
```json
{\"name\": <function-name>, \"arguments\": <args-json-object>}
```'''
def qwen25_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_72B.replace('{tools_desc}', '\n'.join([json.dumps(t, ensure_ascii=False) for t in tools]) )
    system_content +=f'{format_desc}## If all the above tools are not suitable, you must output: Sorry, no tool is suitable for your request.\n\nLet\'s start!'
    sys_prefix, user_prefix = '<|im_start|>system\n', '<|im_end|>\n<|im_start|>user\n'
    user_suffix = '<|im_end|>\n<|im_start|>assistant\n'
    
    return sys_prefix + system_content + user_prefix + query + user_suffix, output

# GLM-4模型输入
system_GLM = '''你是一个名为 GLM-4 的人工智能助手。你是基于智谱AI训练的语言模型 GLM-4 模型开发的，你的任务是针对用户的问题和要求提供适当的答复和支持。 # 可用工具
{tools_desc}
在调用上述函数时，请使用 Json 格式表示调用的参数。'''
# ```json
# {\"name\": <function-name>, \"arguments\": <args-json-object>}
# ```
def GLM_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_GLM.replace('{tools_desc}', '\n'.join([json.dumps(t, indent=4, ensure_ascii=False) for t in tools]) )
    # system_content +=f'{format_desc}## If all the above tools are not suitable, you must output: Sorry, no tool is suitable for your request.\n\nLet\'s start!'
    sys_prefix, user_prefix = '[gMASK] <sop> <|system|>\n', '<|user|>\n'
    user_suffix = '<|assistant|>\n'
    
    return sys_prefix + system_content + user_prefix + query + user_suffix, output

# Hammer模型输入
system_hammer = '''<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n[BEGIN OF TASK INSTRUCTION]\nYou are a tool calling assistant. In order to complete the user's request, you need to select one or more appropriate tools from the following tools and fill in the correct values for the tool parameters. Your specific tasks are:\n1. Make one or more function/tool calls to meet the request based on the question.\n2. If none of the function can be used, point it out and refuse to answer.\n3. If the given question lacks the parameters required by the function, also point it out.\n\nThe following are characters that may interact with you\n1. user: Provides query or additional information.\n2. tool: Returns the results of the tool calling.\n\n[END OF TASK INSTRUCTION]\n\n[BEGIN OF AVAILABLE TOOLS]\n{tools_desc}\n[END OF AVAILABLE TOOLS]\n\n[BEGIN OF FORMAT INSTRUCTION]\n\nThe output MUST strictly adhere to the following JSON format, and NO other text MUST be included.\nThe example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please directly output an empty list '[]'\n```\n[\n    {\"name\": \"func_name1\", \"arguments\": {\"argument1\": \"value1\", \"argument2\": \"value2\"}},\n    ... (more tool calls as required)\n]\n```\n\n[END OF FORMAT INSTRUCTION]\n\n<|im_end|>\n<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n'''
def hammer_model_input(query,tools,output):  # {'system':, 'instruction':, 'input':, 'output':} 四个字段
    system_content = system_hammer.replace('{tools_desc}', json.dumps(tools, ensure_ascii=False) )
    
    return system_content.replace('{query}', query), output