# USAGE: awk -f main.awk regex_templates.csv "${LOG_FILE}" >"${OUT_CSV}"

BEGINFILE {
    if (FNR == NR) { FS = "!" } else { FS = " " }
}

FNR == NR {
    event_template[$1] = $2
    description[$1] = $3
    next
}

{
    sub(/:$/, "", $6)
    line = FNR "," $1 "," $2 "," $3 "," $4 "," $5 "," $6 ","
    for (eventID in event_template) {
        if ($0 ~ (event_template[eventID] "$")) {
            match($0, event_template[eventID] "$", matched_part)
            gsub("\"", "\"\"", matched_part[0])

            if ( index(matched_part[0], ",") > 0 || index(matched_part[0], "\"") > 0 ) {
                print line "\"" matched_part[0] "\"" "," eventID "," description[eventID]
            } else {
                print line matched_part[0] "," eventID "," description[eventID]
            }
            break
        }
    }
}

