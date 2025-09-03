nohup python run_model.py \
	--input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2020/10/ \
	--output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ \
	--model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" > logs/nohup_run_model_2020_10.out &

