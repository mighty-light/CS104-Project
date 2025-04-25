BEGIN {
    start_present = mode % 2
    end_present = int(mode / 2)
    split(from_date, from, ":")
    split(to_date, to, ":")

    # Note that year is not mentioned in the logs
    # ignoring the time that is in milliseconds
    # because it would uglify the entire code 
    # without adding too much practical value

    from_time = from[4] ":" from[5] ":" from[6]
    to_time = to[4] ":" to[5] ":" to[6]

    month["Jan"] = "01"
    month["Feb"] = "02"
    month["Mar"] = "03"
    month["Apr"] = "04"
    month["May"] = "05"
    month["Jun"] = "06"
    month["Jul"] = "07"
    month["Aug"] = "08"
    month["Sep"] = "09"
    month["Oct"] = "10"
    month["Nov"] = "11"
    month["Dec"] = "12"

}

FNR == 1 { print $0 }

FNR > 1 {
    print_line = 1
    split($2, month_date, "-")
    split($3, time, ".")

    # The following hold for the format of structured Android logs
    # year = NOT_SPECIFIED
    # month = month_date[1]
    # date = month_date[2]
    # hour:min:sec = time[1]

    if (start_present) {
        if ( month_date[1] < month[from[2]] ) { print_line = 0 }
        else if ( month_date[1] == month[from[2]] ) {
            if ( month_date[2] < from[3] ) { print_line = 0 }
            else if ( month_date[2] == from[3] ) {
                print_line = time[1] >= from_time
            }
        }
    }
    

    if (end_present) {
        if ( month_date[1] > month[to[2]] ) { print_line = 0 }
        else if ( month_date[1] == month[to[2]] ) {
            if ( month_date[2] > to[3] ) { print_line = 0 }
            else if ( month_date[2] == to[3] ) {
                print_line = time[1] <= to_time
            }
        }
    }

    # Ignoring the year information as it does not exist in the
    # android log file -- perhaps that would be too many logs

    if (print_line) { print $0 }
}
