echo "Training..."

python train_tm.py -o tm data/OPUS_en_it_europarl_train_5K.txt data/EN.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt data/IT.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt


echo "Testing standard NN retrieval (baseline)"

python test_tm.py tm.txt data/OPUS_en_it_europarl_test.txt data/EN.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt data/IT.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt


echo "Testing GC retrieval with 5000 aditional elements"

python -c 5000 test_tm.py tm.txt data/OPUS_en_it_europarl_test.txt data/EN.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt data/IT.200K.cbow1_wind5_hs0_neg10_size300_smpl1e-05.txt 




