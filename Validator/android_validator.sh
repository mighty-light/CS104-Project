#!/bin/bash

LOG_FILE="$1"

date_regex="[01][0-9]-[0-3][0-9] [0-2][0-9]:[0-5][0-9]:[0-5][0-9]\.[0-9][0-9][0-9]"
id_regex="[ 0-9][0-9][0-9][0-9][0-9] [ 0-9][0-9][0-9][0-9][0-9]"
component_and_content="[A-Z][a-zA-Z]+: .*"

regex="${date_regex} ${id_regex} [A-Z] ${component_and_content}"

line_count=$(wc -l "${LOG_FILE}" | cut -d " " -f1)
grep_count=$(grep -c -E "${regex}" "${LOG_FILE}")

# Two cases because the file may or may not end with a newline.
# wc -l would only count the last line if it ends with a newline.

if [[ $grep_count == 0 ]]; then
  exit 1
fi

if [[ $line_count != $grep_count ]] && [[ $((line_count+1)) != $grep_count ]]; then
  exit 1
fi
