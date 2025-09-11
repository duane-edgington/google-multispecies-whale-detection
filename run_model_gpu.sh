nohup python run_model_gpu.py \
	--input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/04/ \
	--output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2018/04/ \
	--model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" > logs/nohup_run_model_2018_04_gpu.out &

