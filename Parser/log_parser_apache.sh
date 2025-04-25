#!/bin/bash

#TODO: IMPLEMENT THE CASE WHEN APACHE LOG EVENT DOES NOT MATCH ANY OF E1-6

LOG_FILE="$1"
OUT_CSV="csv/$(basename "${LOG_FILE}")_structured.csv"

####################
# Make .csv file   #
####################
# The idea is to convert the first two [] in the Apache log file into {}
# and use that latter as fields because the former are used to display the
# E4 message (the only thing involving [])

TEMP_LOG_FILE="${LOG_FILE}.tmp"
sed 's/\[/{/; s/\[/{/; s/\]/}/; s/\]/}/' "${LOG_FILE}" >"${TEMP_LOG_FILE}"
awk -F "[{}]" '{ print $2 "," $4 "," $5 }' "${TEMP_LOG_FILE}" >"${OUT_CSV}"
sed -i "s/ *, */,/g" "${OUT_CSV}" # Remove extra spaces around commas
rm "${TEMP_LOG_FILE}"

####################
# Add line numbers #
####################
awk '{ print FNR","$0 }' "${OUT_CSV}" >tmp
cat tmp >"${OUT_CSV}"
rm tmp

####################
# Add event id etc #
####################
awk -f Parser/add_event_info_apache.awk "${OUT_CSV}" >tmp
cat tmp >"${OUT_CSV}"
rm tmp

####################
# Add col headings #
####################
sed -i '1iLineId,Time,Level,Content,EventId,EventTemplate' "${OUT_CSV}"

####################
# Remove \r ending #
####################
sed -i 's/\r//g' "${OUT_CSV}"
