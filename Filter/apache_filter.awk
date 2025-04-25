BEGIN {
    start_present = mode % 2
    end_present = int(mode / 2)
    split(from_date, from, ":")
    split(to_date, to, ":")

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
    split($2, ldate, " ")

    # The following hold for the format of structured Apache logs
    # year = ldate[5]
    # month = month[ldate[2]]
    # date = ldate[3]
    # hour:min:sec = ldate[4]

    if (start_present) {
        if ( ldate[5] < from[1] ) { print_line = 0 }
        else if ( ldate[5] == from[1] ) {
            if ( month[ldate[2]] < month[from[2]] ) { print_line = 0 }
            else if ( month[ldate[2]] == month[from[2]] ) {
                if ( ldate[3] < from[3] ) { print_line = 0 }
                else if ( ldate[3] == from[3] ) {
                    print_line = ldate[4] >= from_time
                }
            }
        }
    }
    

    if (end_present) {
        if ( ldate[5] > to[1] ) { print_line = 0 }
        else if ( ldate[5] == to[1] ) {
            if ( month[ldate[2]] > month[to[2]] ) { print_line = 0 }
            else if ( month[ldate[2]] == month[to[2]] ) {
                if ( ldate[3] > to[3] ) { print_line = 0 }
                else if ( ldate[3] == to[3] ) {
                    print_line = ldate[4] <= to_time
                }
            }
        }
    }

    if (print_line) { print $0 }
}