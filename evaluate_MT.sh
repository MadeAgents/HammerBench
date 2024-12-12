# log_dir="logs/Meta-Llama-3.1-70B-Instruct-GPTQ-INT4"
# "logs/Meta-Llama-3.1-8B-Instruct"
log_dir=$1
# log_dir="logs/GPT-4o"
python evaluate.py $log_dir/HammerBench_Based/ en
wait
sleep 5
test_type="HammerBench_mQmA"
echo $test_type
python evaluation/align_msg.py $log_dir/ 'HammerBench_mQmA'
python evaluate.py $log_dir/$test_type/MT0/ en
wait
sleep 5
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_mQsA"
echo $test_type
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_sQmA"
echo $test_type
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_SO_case1"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ en
wait
sleep 5
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_SO_case2"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ en
wait
sleep 5
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_mSv"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ en
wait
sleep 5
python evaluate.py $log_dir/$test_type/ en
wait
sleep 5
test_type="HammerBench_External"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ en
wait
sleep 5
python evaluate.py $log_dir/$test_type/ en