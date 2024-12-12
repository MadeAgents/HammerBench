# log_dir="logs/en/GPT-4o"
log_dir=$1
# "en"
language=$2
echo "single-turn"
test_type="ST_Perfect"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="ST_Imperfect"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="ST_External"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="ir_ST_Perfect"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="ir_ST_Imperfect"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="ir_ST_External"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5

echo "multi-turn"
python evaluate.py $log_dir/HammerBench_Based/ $language 'all'
wait
sleep 5
test_type="HammerBench_mQmA"
echo $test_type
python evaluation/align_msg.py $log_dir/ 'HammerBench_mQmA'
python evaluate.py $log_dir/$test_type/MT0/ $language 'all'
wait
sleep 5
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_mQsA"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_sQmA"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_SO_case1"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ $language 'all'
wait
sleep 5
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_SO_case2"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ $language 'all'
wait
sleep 5
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_mSv"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ $language 'all'
wait
sleep 5
python evaluate.py $log_dir/$test_type/ $language 'all'
wait
sleep 5
test_type="HammerBench_External"
echo $test_type
python evaluation/align_msg.py $log_dir/ $test_type
python evaluate.py $log_dir/$test_type/MT0/ $language 'all'
wait
sleep 5
test_type="HammerBench_IS"
echo $test_type
python evaluate.py $log_dir/$test_type/ $language '-1'