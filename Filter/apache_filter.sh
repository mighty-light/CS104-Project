#!/bin/bash

mode="$1"
csv_file="$2"
output_file="$3"
start_date="$4"
end_date="$5"

awk -F "," -f Filter/apache_filter.awk -v mode="${mode}" -v from_date="${start_date}" -v to_date="${end_date}" "${csv_file}" >"${output_file}"
