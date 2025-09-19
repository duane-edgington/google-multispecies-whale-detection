# Detecting Whale Song

Applying the Google/kaggle multispecies Whale Detector on Pacific Ocean Sound data.

References:

- <https://www.kaggle.com/models/google/multispecies-whale>
- <https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2024.1394695/full>

Some notebooks where code developed here has been used:

- <https://colab.research.google.com/drive/1vA-wVOc9bHrNlZ7Wj0mauwyqlmV5ZkuA>
- <https://colab.research.google.com/drive/13HinPes8vi39yjb7nD3ZULpB3eXZFxvc>
- <https://colab.research.google.com/drive/11gxYzDKPgyqncu1ooiTrH-iWtemkFIJJ>

See also: <https://docs.mbari.org/pacific-sound/>.

## Setup

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -r requirements.txt

In subsequent sessions, just run `source venv/bin/activate`
to activate the python environment.

## Want to use this on your machine?

Running Google Multispecies-whale kaggle model on PAM Archive data



Go into working directory    

   source venv/bin/activate 

   export TFHUB_CACHE_DIR="./local/"

If need to generate resampled 24kHz files from PAM archive, run          

new_resample_sox.sh

example:

      nohup ./new_resample_sox.sh 2020 10 > logs/nohup_resample_2020_10.out &

These will go to  /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz/ 

If need to generate 5 sec chunk files from the resampled 24kHz files, run      
     
      python3 chunk_resampled.py

example:      

      nohup python3 chunk_resampled.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz/2020/10/ > logs/nohup_chunk_2020_10.out &

Args:

input_directory: Input directory path

chunk_duration: Duration of each chunk in seconds
    
Returns:

Processing statistics





run the model over the resampled 5 sec chunks

       python run_model.py --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/04/ --output_dir ./results --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2"

example:

        nohup python run_model.py --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2020/10/ --output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" > logs/nohup_run_model_2020_10.out &

if nvidia cudnn enabled gpu is availalbe, one can run with gpu_enabled version

        nohup python run_model_gpu.py --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2020/10/ --output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" > logs/nohup_run_model_2020_10.out &

optimized nvidia cudnn enabled gpu with batching into gpu memory

	python run_model_gpu_optimized.py    --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/04/     --output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2018/04/        --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2"     --batch_size 256  # Adjust based on your GPU memory

another

	nohup python3 run_model_gpu_optimized.py --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2020/10/ --output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_gpu/2020/10/ --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" --batch_size 256  > logs/nohup_run_model_gpu_optimized_256_2020_10.out &

test with just one directory, and output to a test directory

	nohup python run_model_gpu.py \
            --input_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz_chunks/2018/04/MARS_20180413_235913_resampled_24kHz/ \
            --output_dir /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/test/ \
            --model_url "https://www.kaggle.com/models/google/multispecies-whale/TensorFlow2/default/2" > logs/nohup_run_model_2018_04_onedir_gpu_6.out &

check run status with htop

         htop

if conda has confused the system htop with one of its own copies:

         LD_LIBRARY_PATH=/usr/lib:/usr/lib64 /usr/bin/htop
or

         export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH htop
         
to convert json output to a csv file (one file per directory)

      python3 json_to_csv_expanded_natsort.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/2018/04/scores/MARS_20180420_224913_resampled_24kHz  MARS_20180405_105913.csv


### convert the json output files to a csv files, lists expanded so that each key and value is in a separate column

# Basic usage - automatic output filename
     python json_to_csv_expanded_natsort.py MARS_20180413_065913_resampled_24kHz

# With custom output filename
     python json_to_csv_expanded_natsort.py MARS_20180413_065913_resampled_24kHz -o results.csv

# With custom output path and verbose mode
     python json_to_csv_expanded_natsort.py /path/to/data -o /output/path/processed_data.csv -v

# Show help
     python json_to_csv_expanded_natsort.py --help

# iterate over all the directories

     ./process_all_json_to_csv_sinc.sh /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_sinc/2018/04/

# another exaample
       nohup ./process_all_json_to_csv.sh /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ > logs/nohup_process_all_json_to_csv_2020_10.out &

### convert to csv files containing only epoch time of score (beginning of wav file analyzed) and model output score for one class

      extract_epoch_key_scores.py 

script to iterate over the csv files

       process_all_key_scores.sh
# example
       nohup ./process_all_key_scores.sh /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_sinc/2018/04 Oo > logs/nohup_scores_sinc_2018_04.out &
# another example
       nohup ./process_all_key_scores.sh /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ Mn > logs/nohup_scores_mn_2020_10.out &

pattern

       ./process_all_key_scores.sh /path/to/scores Mn

       ./process_all_key_scores.sh /path/to/scores Bm

       ./process_all_key_scores.sh /path/to/scores Whistle

       ./process_all_key_scores.sh /path/to/scores Upcall


# display the number of directories in a particular directory 
useful to display how many output directories of score json files is generated. Should equal the number of starting .wav files

       find /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/10/ -maxdepth 1 -mindepth 1 -type d | wc -l

## analysis of results
Program to create plots of scores in a period

Histogram of distribution of scores (from 0 to 1)

Histogram of log(10) of distribution of scores

Scatter plot of class score vs time

Distibution of class score 

Statistics (number of samples, etc)

       python whale_analyzer.py /path/to/csv/files --name-pattern "epoch_oo_scores" --bins 20 --output analysis.png

Example

    python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2018/04 \
           --name-pattern "epoch_oo_scores" --bins 10 --time-period "10min" \
           --output /mnt/PAM_Analysis/test/analysis_scores_2018_04.png

another example

    python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2020/11 \
           --name-pattern "epoch_mn_scores" --bins 10 --time-period "60min" \
           --output /mnt/PAM_Analysis/test/analysis_scores_mn_2020_11.png

an example with all points plotted on scatter plots

    python3 whale_analyzer.py /mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores/2018/05 \
        --name-pattern "epoch_oo_scores" --bins 10 --time-period "60min" \
        --output /mnt/PAM_Analysis/test/analysis_scores_oo_2018_05_a.png \
        --plot3-samples 600000 --plot5-samples 600000

# Use default sample sizes (10,000 for plot 3, 100,000 for plot 5)
       python whale_analyzer.py /path/to/files --name-pattern "epoch_oo_scores"

# Custom sample sizes
       python whale_analyzer.py /path/to/files --name-pattern "epoch_oo_scores" --plot3-samples 5000 --plot5-samples 50000

# High resolution with more samples
       python whale_analyzer.py /path/to/files --name-pattern "epoch_oo_scores" --plot3-samples 20000 --plot5-samples 200000

# Lower resolution for faster processing
       python whale_analyzer.py /path/to/files --name-pattern "epoch_oo_scores" --plot3-samples 2000 --plot5-samples 20000

<img width="5371" height="5889" alt="analysis_scores_bp_2020_11" src="https://github.com/user-attachments/assets/33b94098-8295-47b8-9f6b-c91b8916fff6" />

## below needs update

Default settings and examples below are mainly in terms of our own setup on
a particular machine ("gizo"), where `/mnt/PAM_Analysis/` is a base directory
for various locations.
Although some scripts here accept options to set relevant locations,
you may also find convenient to directly adjust the
`DEFAULT_AUDIO_BASE_DIR` and `DEFAULT_SCORE_BASE_DIR` settings
in [hwsd/file_helper.py](hwsd/file_helper.py).

## Gizo

On gizo, a copy of the code in this repo is located under
`/opt/humpback/humpback-whale-song-detection/`. 

Base directories:

- `/mnt/PAM_Analysis/decimated_16kHz/` - Input audio files sampled at 16kHz

- `/mnt/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz/` - Input audio files resampled to 10kHz

- `/mnt/PAM_Analysis/GoogleHumpbackModel/Scores/` - Generated score files

With 2016-11-01 as an example:

`/mnt/PAM_Analysis/GoogleHumpbackModel/Scores/2016/11/Scores-20161101.npy`

will be the model score file corresponding to the audio file:

`/mnt/PAM_Analysis/decimated_16kHz/2016/11/MARS-20161101T000000Z-16kHz.wav`

via the intermediate, decimated 10kHz version at:

`/mnt/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz/2016/11/MARS-20161101T000000Z-10kHz.wav`

## Resampling to 10kHz

Note that the NOAA/Google model requires the input signal to be sampled at 10kHz.

We do the necessary resampling beforehand using [`sox`](http://sox.sourceforge.net/). 

- `resample_sox.sh`:
  For a given year and month, this script starts multiple `sox`
  processes concurrently, one for each day of the month. Example:

        ./resample_sox.sh 2018 11

- `resample_year_months.sh`:
  A convenient script that runs `resample_sox.sh` in sequence for all
  given months in a given year.
  For example, to resample Jan–Oct'2018:

        ./resample_year_months.sh 2018 $(seq 1 10)

A recent resampling exercise on gizo (Sept to Dec, 2021):

    cd /opt/humpback/humpback-whale-song-detection
    nohup ./resample_year_months.sh 2021 $(seq 9 12) > logs/nohup_resample_2021_9_to_12.out &

    nohup ./resample_year_months.sh 2022 $(seq 1 3) > logs/nohup_resample_2022_1_to_3.out &

(ongoing) A more recent resampling exercise on gizo:

    cd /opt/humpback/humpback-whale-song-detection
    mkdir -p logs
    nohup ./resample_year_months.sh 2023 $(seq 1 1) > logs/nohup_resample_2023_1_to_1.out &

## Applying the model

Run `hwsd/apply_model.py` indicating the years, months, and days to process.

Usage:

    hwsd/apply_model.py time-interval ...

where each time interval must be of the form
`yearRange/monthRange/dayRange` or `yearRange/monthRange`,
with each range fragment either a single number or a hyphen-separated
range with inclusive limits. If omitted, the day range will be "1-31".
The code takes care of adjusting the day range depending on the calendar month.

Example: To apply the model on the six months Oct–Dec'2020 and Jan–Mar'2021:

    hwsd/apply_model.py "2020/10-12" "2021/1-3"

Some of our runs on gizo have been like the following:

    source venv/bin/activate
    export PYTHONPATH=.
    mkdir -p logs

Two concurrent jobs to process Jan–Aug'2021:

    nohup python3 -u hwsd/apply_model.py "2021/1-4" > logs/nohup-2021--1-4.out &
    nohup python3 -u hwsd/apply_model.py "2021/5-8" > logs/nohup-2021--5-8.out &

Four concurrent jobs (one per month) to process Sept–Dec'2021:

    for mr in 9 10 11 12; do
        nohup python3 -u hwsd/apply_model.py "2021/$mr" > "logs/nohup-2021--$mr.out" &
    done

Five concurrent jobs to process Jan–Oct'2018:

    for mr in 1-2 3-4 5-6 7-8 9-10; do
        nohup python3 -u hwsd/apply_model.py "2018/$mr" > "logs/nohup-2018--$mr.out" &
    done

Four concurrent jobs to process 2017:

    for mr in 1-3 4-6 7-9 10-12; do
        nohup python3 -u hwsd/apply_model.py "2017/$mr" > "logs/nohup-2017--$mr.out" &
    done

NOTE: 
`hwsd/apply_model.py` is mainly a convenience to run the actual core function
`apply_model_day` on multiple days. In particular, note that `HOURS_PER_CALL`
and `MODEL_MINUTES` are two key settings that you may need to adjust depending
on available memory on the system. See `hwsd/apply_model.py` for more details. 

You can also run `hwsd/apply_model_day.py` directly and with options from the
command line to set any relevant parameters as needed.
Run the following for usage:

    hwsd/apply_model_day.py --help

## Generating plots

This repo also includes code to generate plots with spectrograms and scores,
which mainly helped with initial validations.

In this case, no command line arguments are expected.
Edit `hwsd/plot_scores.py` as needed to indicate the
years, months, and days to process. Then, run it:

    hwsd/plot_scores.py

Each generated plot file will be located next to the corresponding score file.

Note that `hwsd/plot_scores.py` is a convenience to run the actual core function
`plot_scores_day` on multiple days. 
For a particular day you can also run `hwsd/plot_scores_day.py` directly.
Run the following for usage:

    hwsd/plot_scores_day.py --help

---

## Development

With the setup in place, run the following on a regular basis
as you work with the code:

    make

The default task in the makefile does type checking, testing and code formatting.

**NOTE**: Before committing/pushing any changes, be sure to also run:

    make pylint

and address any issues, or check with the team about any known pylint complaints.

See [`makefile`](makefile) for all available tasks.
