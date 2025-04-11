# TO BE CALLED USING: awk -F "!"

FNR==NR {
    regex[$1] = $2
    next
}

{
    for (e in regex) {
        if ($0 ~ regex[e]) {
            print $0 "," e
            break
        }
    }
}

# TARGET FILES: new_syslog_rules.txt Linux_2k.log

