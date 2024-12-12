# HammerBench

The source code and dataset mentioned in the paper [**HammerBench: Fine-Grained Evaluation for Function-Calling with Multi-turn Human-LLM Interactions**](https://arxiv.org/pdf/).

## Overview
**HammerBench** is a benchmark that closely aligned with realworld slot-filling tasks in interactive dialogues. You can evaluate the performance of LLMs under various circumstances as follows:
- **imperfect instruction** :The user query that only gives few required parameter values.
- **diverse question-answer trajectories** :users may provide more or fewer responses about missing arguments than expected.
- **intent/argument shifts** :users may frequently modify their intents or arguments due to errors or other reasons during the interaction;
- **external individual information** : users may refer to external individual information indirectly, often using pronouns instead of directly specifying slot values.

Some examples are shown in the figure:
<div align="center">
<img src="imgs/example datasets.png" width="1000px">
</div>


The comparison between the existing and our benchmarks is as follows:
<div align="center">
<img src="imgs/comparison.png" width="1000px">
</div>

## Data Construction
The construction methodology of our datasets is illustrated in the following diagram:
<div align="center">
<img src="imgs/generation pipline.png" width="1000px">
</div>
- **toolset construction** : The construction of the toolset was inspired by selecting the most popular apps from the APP Store. We use LLMs to initially generate descriptions of tool descriptions, then manually revised. Subsequently, JSON format tools are generated based on these descriptions. The entire process includes multiple rounds of manual inspection and correction, ultimately resulting in a toolset comprising 1,063 tools.
- **basic data construction** : Based on the self-instruct method we further generate instances by outputing arguments first and then queries, and strictly controll the parameters that appear in the generated arguments. Additionally, we designed an LLM-based check module to filter out low-quality data, and manually completed the error data.
- **fine-grained data construction** : For example, 'External individual information' module can convert any query-label pairs into the dataset containing external individual information. And we also generate datasets about diverse Q&A trajectories and intent/argument shifts. 

For more details, please refer to our paper.

## Data
All of our datasets are in "data/en/", use the shareGPT format.
```
{
      'messages':[
            {
                  'role':'user'
                  'content':'user query'
            },
            {
                  'role':'function call'
                  'content':{'name': <function name>,'arguments': <arguments>}
            }
            ...
      ],
      'multiple_tools':<candidate tools>,
      'single_tool':<ground truth function information>
}
```

The detail descriptions of different data types are in our paper. They are saved in:

ST_Perfect : data/en/single-turn/ST_Perfect.json
ST_Imperfect : data/en/single-turn/ST_Imperfect.json
ST_External : data/en/single-turn/ST_External.json
irrelevant : data/en/single-turn/(ir_ST_External.json, ir_ST_Perfect.json, ir_ST_Imperfect.json)
sQsA : data/en/multi-turn/HammerBench_Based.json
mQmA : data/en/multi-turn/HammerBench_mQmA.json
mQsA : data/en/multi-turn/HammerBench_mQsA.json
sQmA : data/en/multi-turn/HammerBench_sQmA.json
IS : data/en/multi-turn/HammerBench_IS.json
SO : data/en/multi-turn/HammerBench_SO_case1.json(SO_case2.json)
mSv : data/en/multi-turn/HammerBench_mSv.json
External : data/en/multi-turn/HammerBench_External.json

All datasets are transformed from the 'HammerBench_Based.json' in the sQsA format. Since not all sQsA data can be converted, it is necessary to record the indices of the sQsA data involved in different types of conversions( data/en/multi-turn/correspond_id). For example, 'correspond_id_mSv.json' records the indices about 'HammerBench_mSv.json'. Also, the files in 'data/en/multi-turn/snapshot_id' record the id of turn for SO and External transformation occuring to evaluate the snapshots at the moment of slot overriding(SO) and answering with pronouns(External).

As for Chinese dataset, please see 'data/zh'.

## Evaluation
### Install Dependencies

You should install dependencies using the following command:

```
pip install -r requirements.txt
```

### Evaluate the log file inferenced by LLMs
evaluate.py requires two inputs: the MT_0.json file and the MT_res.json file. The logs/GPT-4o/HammerBench_mQmA/MT_0.json and data/en/multi-turn/HammerBench_mQmA.json are the same. And the item of MT_res.json is as follows:
```
{
      "input": "user:Check if my car has any illegal records\nassistant:What city is the violation located in?\nuser:The violating city is Guangzhou.\nassistant:Please provide the license plate number\nuser:My license plate number is Yue B67890.",
      "predict": "```json\n{\"name\": \"Navigation.TrafficViolations.queryViolation\", \"parameters\": {\"plate_number\": \"Yue B67890\", \"city\": \"Guangzhou\", \"time\": \"\"}}\n```",
      "label": {
      "name": "Navigation.TrafficViolations.queryViolation",
            "arguments": {
            "city": "Guangzhou",
            "plate_number": "Yue B67890"
            }
      }
}
```

Use the following command for evaluation:

```
bash evaluate_MT.sh <log_dir>
```

For example, to evaluate the GPT-4o model:

```
bash eval.sh logs/GPT-4o
```


Same to the evaluation of single-turn results:
```
python evaluate.py <log_dir> en
```

After recording the results(e.g. GPT-4o.log) obtained from the previous bash commands, it can be conveniently converted into a dataframe through logs/log2df.py.
```
python log2df.py GPT-4o.log
```

If you need to adapt the post-processing for different output formats, please modify evaluation/process_output.py.


## Citation

If you use HammerBench, please cite our paper:
```
@misc{hammerbench,
      title={HammerBench: Fine-Grained Evaluation for Function-Calling with Multi-turn Human-LLM Interactions}, 
      author={},
      year={2024},
      eprint={},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/}, 
}
```