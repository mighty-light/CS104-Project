{
  match($5,/^([^[]+)\[([0-9]+)\]:$/,comp_and_pid) 
  if (comp_and_pid[1] == "") {
    comp_and_pid[1] = $5
    sub(/:$/, "", comp_and_pid[1])
  }

  if (comp_and_pid[1] == "--") {
    xyz = comp_and_pid[1] " " $6
    match(xyz,/^([^[]+)\[([0-9]+)\]:$/,comp_and_pid) 
  }

  s = FNR "," $1 "," $2 "," $3 "," $4 "," comp_and_pid[1] "," comp_and_pid[2] ","

  match($0, /^[^:]*:[^:]*:[^:]*: *(.*)/, content)
  t = content[1]
  sub(/ $/, "", t)
  
  if ( index(t, ",") > 0 ) {
    print s "\"" t "\""
  } else {
    print s t
  }
}
