python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04 \
        --name-pattern "epoch_oo_scores" --bins 10 --time-period "60min" \
        --output /mnt/PAM_Analysis/test/analysis_scores_oo_2018_04_gpu_a.png \
        --plot3-samples 600000 --plot5-samples 600000
read -n 1 -s -r -p "Press any key to continue..."
python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04 \
        --name-pattern "epoch_mn_scores" --bins 10 --time-period "60min" \
        --output /mnt/PAM_Analysis/test/analysis_scores_mn_2018_04_gpu_a.png \
        --plot3-samples 600000 --plot5-samples 600000
read -n 1 -s -r -p "Press any key to continue..."
python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04 \
        --name-pattern "epoch_bm_scores" --bins 10 --time-period "60min" \
        --output /mnt/PAM_Analysis/test/analysis_scores_bm_2018_04_gpu_a.png \
        --plot3-samples 600000 --plot5-samples 600000
read -n 1 -s -r -p "Press any key to continue..."
python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04 \
        --name-pattern "epoch_bp_scores" --bins 10 --time-period "60min" \
        --output /mnt/PAM_Analysis/test/analysis_scores_bp_2018_04_gpu_a.png \
        --plot3-samples 600000 --plot5-samples 600000

