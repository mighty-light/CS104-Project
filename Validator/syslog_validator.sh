#!/bin/bash

LOG_FILE="$1"

regex='^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ 1-3][0-9] [0-9]{2}:[0-5][0-9]:[0-5][0-9] .*'

line_count=$(wc -l "${LOG_FILE}" | cut -d " " -f 1)
grep_count=$(grep -c -E "${regex}" "${LOG_FILE}")

if [[ $grep_count == 0 ]]; then
  exit 1
fi

if [[ "$line_count" != "$grep_count" ]] && [[ $((line_count + 1)) != "$grep_count" ]]; then
  exit 1
fi
