#!/bin/bash

LOG_FILE="$1"
OUT_CSV="csv/$(basename "${LOG_FILE}")_structured.csv"

####################
# Remove \r ending #
####################
sed -i 's/\r//g' "${LOG_FILE}"

####################
# Protect syslod 1.#
####################
sed -i -E 's/syslogd ([0-9]\.[0-9]\.[0-9])/syslogd-\1/g' "${LOG_FILE}"

####################
# Make .csv file   #
####################
awk -f Parser/noregex_syslog.awk "${LOG_FILE}" >"${LOG_FILE}.tmp1"
awk -F "!" -f Parser/regex_syslog.awk Parser/new_syslog_rules.txt "${LOG_FILE}.tmp1" >"${LOG_FILE}.tmp2"
awk -F "!" -f Parser/add_event_info_syslog.awk Parser/raw_syslog_rules.txt "${LOG_FILE}.tmp2" >"${OUT_CSV}"
rm "${LOG_FILE}.tmp1" "${LOG_FILE}.tmp2"

####################
# Add col headings #
####################
sed -i -E 's/syslogd-([0-9]\.[0-9]\.[0-9])/syslogd \1/g' "${LOG_FILE}"
sed -i -E 's/syslogd-([0-9]\.[0-9]\.[0-9])/syslogd \1/g' "${OUT_CSV}"
sed -i '1iLineId,Month,Date,Time,Level,Component,PID,Content,EventId,EventTemplate' "${OUT_CSV}"
