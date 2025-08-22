#!/usr/bin/env bash

# This script runs `sox` for resampling all days in a given year/month,
# which are required arguments. Example:
#    ./resample_sox.sh 2018 11
# Each resample is launched in its own process.

set -ue

year=$1
month=$2
days=$(seq 1 31)  # for convenience 1–31 regardless of month

audio_base_dir="/mnt/PAM_Archive"

decimated_base_dir="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/resampled_24kHz"
#decimated_base_dir="/home/duane/google-multispecies-whale-detection/local/PAM_Analysis/GoogleOrcaModel/resampled_24kHz"

days_line="$(echo "${days}" | tr '\n' ' ')"

in_dir=$(printf "%s/%04d/%02d" ${audio_base_dir} "${year}" "${month}")

out_dir=$(printf "%s/%04d/%02d" ${decimated_base_dir} "${year}" "${month}")
mkdir -p "${out_dir}"

printf "Starting resample_sox.sh: %04d-%02d days: %s\n" "${year}" "${month}" "${days_line}"

#use SoX to resample the audio data directly. 
# rate converts to 24kHz. the -v flag is for very high quality.
# convert to 16 bit depth high (required by the google model)
# highpass 10Hz (to remove dc offset)
# vol 3 (to adjust volume 3x, making the signal correct in Volts)
# fade logarithmic 0.1 sec fade in, 600 sec hold (i.e. full duration of 10 minutes), 0.1 sec fade out

for day in ${days}; do
  prefix=$(printf "%s/MARS_%04d%02d%02d" "${in_dir}" "${year}" "${month}" "${day}")
  #for infile in "${prefix}"_06*.wav; do
  for infile in "${prefix}"_*.wav; do
    basename=$(basename "${infile}" .wav)
    outfile="${out_dir}/${basename}_resampled_24kHz.wav"
    echo "infile = ${infile}"
    echo "outfile = ${outfile}"
    sox "${infile}" -b 16 "${outfile}" rate -v 24000 highpass 10 fade 0.1 600 0.1 vol 3 &
  done

done
wait
