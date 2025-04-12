#!/bin/bash

LOG_FILE="$1"
OUT_CSV="${LOG_FILE}_structured.csv"

###################
# Safety measures #
###################
sed -i 's/\r//g' "${LOG_FILE}"

####################
# Call main script #
####################
awk -f Parser/main.awk Parser/with_desc_regex_templates.csv "$LOG_FILE" >"${OUT_CSV}"

####################
# Add heading      #
####################
sed -i '1iLineId,Date,Time,Pid,Tid,Level,Component,Content,EventId,EventTemplate' "${OUT_CSV}"
