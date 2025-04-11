#!/bin/bash

# NOTE: ALL APACHE LOG EVENT IN THE SAMPLE MATCH E1-6 SO NO BLANK EVENTS ARE 
# IMPLEMENTED IN THE VALIDATOR. IT ONLY MAKES IT HARDER TO CHECK FOR VALIDITY.

LOG_FILE="$1"

data_regex="\
^\[\
(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \
(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \
[0-3][0-9] \
[0-2][0-9]:[0-5][0-9]:[0-5][0-9] \
[1-2][0-9][0-9][0-9]\
\]\
"
level="\[(notice|error)\]"
content_regex="\
(jk2_init\(\) Found child [0-9][0-9]* in scoreboard slot [0-9][0-9]*|\
workerEnv\.init\(\) ok .*|\
mod_jk child workerEnv in error state [0-9][0-9]*|\
\[client [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\] Directory index forbidden by rule:|\
jk2_init\(\) Can't find child [0-9][0-9]* in scoreboard|\
mod_jk child init)\
"
regex="${data_regex} ${level} ${content_regex}"

line_count=$(wc -l "${LOG_FILE}" | cut -d " " -f 1)
grep_count=$(grep -c -E "${regex}" "${LOG_FILE}")

# Two cases because the file may or may not end with a newline.
# wc -l would only count the last line if it ends with a newline.

if [[ $grep_count == 0 ]]; then
  exit 1
fi

if [[ $line_count != $grep_count ]] && [[ $((line_count+1)) != $grep_count ]]; then
  exit 1
fi
