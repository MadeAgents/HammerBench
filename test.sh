# "/home/notebook/data/group/model_hub/huggingface/meta-llama/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4"
model_path=$1
language='en'
echo "multi-turn"
python inference.py data/$language/multi-turn/HammerBench_Based.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_mQmA.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_mQsA.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_sQmA.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_SO_case1.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_SO_case2.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_mSv.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_External.json $model_path $language
wait
sleep 5
python inference.py data/$language/multi-turn/HammerBench_IS.json $model_path $language
wait
sleep 5
echo "single-turn"
python inference.py data/$language/single-turn/ST_Perfect.json $model_path $language
wait
sleep 5
python inference.py data/$language/single-turn/ST_Imperfect.json $model_path $language
wait
sleep 5
python inference.py data/$language/single-turn/ST_External.json $model_path $language
wait
sleep 5
python inference.py data/$language/single-turn/ir_ST_Perfect.json $model_path $language
wait
sleep 5
python inference.py data/$language/single-turn/ir_ST_Imperfect.json $model_path $language
wait
sleep 5
python inference.py data/$language/single-turn/ir_ST_External.json $model_path $language