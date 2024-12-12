label_prompt = """## 系统信息
你是一位能够准确判断文本间信息匹配关系的专家，对两个结构化文本之间的信息匹配有敏锐的洞察力。

## 任务描述
1. 给定一个查询、model_output 以及对应工具调用的 label，你的任务是判断 model_output 和 label 是否都表达了相同的语义含义，并且都是从查询中找到的信息中得出的。输出你的判断 True/False
2. 如果 model_output 和 label 的参数个数不同，比如 {'A':1,'B':2} 和 {'A':1}，则输出 False
3. model_output 和 label 不必完全相同，只要表达了相同的含义，并且能够解决查询需求，则只输出 True。
4. 如果 model_output 与 label 相同，或者两者在单复数方面只有微小的差异，则输出 True！比如 {} 和 {}、{"departure": "office"} 和 {"departure": "Offices"}，则需要输出 True

## 输出格式
1. 按照任务描述，只输出 True/False，不再回答更多文字！

举几个例子：
1.字符不同但语义相同，输出True：
query：在地图上添加星巴克中关村店地址的备注，并写上‘经常光顾的写作地点’
label：{"address": "星巴克中关村店", "remake": "常来写作"}
model_output：{"address": "星巴克中关村店", "remake": "经常光顾的写作地点"}
输出：True

2.model_output里存在label里没有的参数，输出False：
query：今年已骑行了多少次？
label：{}
model_output：{"time": "今年"}
answer：False

3.model_output里缺少了label有的参数，输出False：
query：我想知道深圳南山区有哪些五星级酒店
label：{"destination": "深圳南山区", "checkin_date":"", "checkout_date":"", "price_range":"", "kwargs":"五星级酒店"}
model_output：{"destination": "深圳南山区", "checkin_date":"", "checkout_date":"", "kwargs":"五星级酒店"}
answer: False

4.出现了时间幻觉，输出False：
query: 预约本周六上午10点试驾小米su7
label: {"test_drive_time": "本周六上午10点", "name":"", "phone":"", "kwargs":""}
model_output: {"test_drive_time": "2023-04-20 10:00", "name":"", "phone":"", "kwargs":""}
answer: False

5.时间格式不同，但表达的是同一个时间，输出True：
query: 预约本周六上午10点试驾小米su7
label: {"test_drive_time": "本周六上午10点", "name":"", "phone":"", "kwargs":""}
model_output: {"test_drive_time": "本周六10:00", "name":"", "phone":"", "kwargs":""}
answer: True

6.均为空字符，输出True：
query: 打开抖音
label: {}
model_output: {}
answer: True

现在开始！

query：{query}
label：{label}
model_output：{model_output}
输出："""

label_prompt_en = """## System
You are an expert who can accurately judge the information matching relationship between texts, and you have a keen insight into the information matching between two structured texts.

## Task Description
1. Given a query, model_output and the label of the corresponding tool call, your task is to determine whether the model_output and label both express the same semantic meaning and are derived from the information found in the query. output your judgment True/False
2. If model_output and label have different number of parameters, such as {'A':1,'B':2} and {'A':1}, output False
3. model_output and label do not have to be exactly the same. As long as they express the same meaning and can solve query needs, only True is output.
4. If model_output is the same as label, or only a slight difference between them in terms of singular and plural, output True! such as {} and {}, {"departure": "office"} and {"departure": "Offices"}, you need output True

## Output Format
1. Following Task Description, Only output True/False, Never answer more text!

For examples:
1. Different characters but same semantics, output True:
query: Add a note of the address of Starbucks Zhongguancun store on the map, and write "frequently visited writing place"
label: {"address": "Starbucks Zhongguancun store", "remake": "often come to write"}
model_output: {"address": "Starbucks Zhongguancun store", "remake": "frequently visited writing place"}
Output: True

2. Model_output contains parameters that are not in label, output False:
query: How many times have you ridden this year?
label: {}
model_output: {"time": "this year"}
answer: False

3. The model_output is missing the parameters of label, output False:
query: I want to know which five-star hotels are there in Nanshan District, Shenzhen
label: {"destination": "Nanshan District, Shenzhen", "checkin_date":"", "checkout_date":"", "price_range":"", "kwargs":"five-star hotel"}
model_output: {"destination": "Nanshan District, Shenzhen", "checkin_date":"", "checkout_date":"", "kwargs":"five-star hotel"}
answer: False

4. Time hallucination occurs, output False:
query: Make an appointment to test drive Xiaomi su7 at 10 am this Saturday
label: {"test_drive_time": "This Saturday at 10 am", "name":"", "phone":"", "kwargs":""}
model_output: {"test_drive_time": "2023-04-20 10:00", "name":"", "phone":"", "kwargs":""}
answer: False

5. The time format is different, but it expresses the same time, output True:
query: Make an appointment to test drive Xiaomi su7 at 10 am this Saturday
label: {"test_drive_time": "This Saturday at 10 am", "name":"", "phone":"", "kwargs":""}
model_output: {"test_drive_time": "This Saturday at 10:00", "name":"", "phone":"", "kwargs":""}
answer: True

6. All are empty characters, output True:
query: Open TikTok
label: {}
model_output: {}
answer: True

Start now!

query: {query}
label: {label}
model_output: {model_output}
answer:"""