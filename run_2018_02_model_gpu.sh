nohup python3 run_model_gpu_optimized.py \
	--input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/02/ \
	--output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/02/ \
	--model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" \
	--batch_size 16  > logs/nohup_run_model_2018_02_gpu_optimized.out &

