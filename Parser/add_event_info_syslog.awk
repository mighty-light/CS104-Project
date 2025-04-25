# TO BE CALLED USING: awk -F "!"

FNR==NR {
    logger[$1] = $2
    next
}

{
    for (e in logger) {
        if ($0 ~ (e "$")) {
            print $0 "," logger[e]
            break
        }
    }
}

# TARGET FILES: raw_syslog_rules.txt Linux_2k.log

