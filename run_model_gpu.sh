nohup python run_model_gpu_optimized.py \
	--input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/04/ \
	--output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04/ \
	--model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" \
	--batch_size 8  # Adjust based on your GPU memory
> logs/nohup_run_model_2018_04_gpu_optimized.out &

