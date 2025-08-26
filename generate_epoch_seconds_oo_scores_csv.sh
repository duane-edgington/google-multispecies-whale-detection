#!/usr/bin/env bash

# This script runs `extract_epoch_oo_scores.py` for resampling all days in a given year/month,
# which are required arguments. Example:
#    ./ generate_epoch_seconds_oo_scores_csv.sh 2018 11
# Each resample is launched in its own process.

set -ue

year=$1
month=$2
days=$(seq 1 31)  # for convenience 1–31 regardless of month

base_dir="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores"

output_base_dir="/mnt/PAM_Analysis/GoogleMultiSpeciesWhaleModel2/scores_csv"
#decimated_base_dir="/home/duane/google-multispecies-whale-detection/local/PAM_Analysis/GoogleOrcaModel/resampled_24kHz"

days_line="$(echo "${days}" | tr '\n' ' ')"

in_dir=$(printf "%s/%04d/%02d" ${base_dir} "${year}" "${month}")

out_dir=$(printf "%s/%04d/%02d" $output_base_dir} "${year}" "${month}")
mkdir -p "${out_dir}"

printf "starting generate_epic_seconds_oo_scores_csv.sh: %04d-%02d days: %s\n" "${year}" "${month}" "${days_line}"

# use extract_epoch_oo_scores.py to extract Oo scores from json files and put into a single csv file






for day in ${days}; do
  prefix=$(printf "%s/MARS_%04d%02d%02d" "${in_dir}" "${year}" "${month}" "${day}")
  #baseprefix = $(printf "
  #for infile in "${prefix}"_06*.wav; do
  for infile in "${prefix}"_resampled_24kHz/${prefix}_resampled_24kHz_${prefix}_*.json; do
    basename=$(basename "${infile}" .json)
    outfile="${out_dir}/${basename}_Oo.csv"
    echo "infile = ${infile}"
    echo "outfile = ${outfile}"
    python3 extract_epic_oo_scores.py "${infile}" &

  done

done
wait
