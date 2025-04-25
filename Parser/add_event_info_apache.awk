#TODO: IMPLEMENT THE CASE WHEN APACHE LOG EVENT DOES NOT MATCH ANY OF E1-6
#NOTE: USING A "FOUND" VARIABLE SEEMS NICE BUT Q IS A BIT AMBIGUOUS
#AMBIGUITY: HOW ARE WE SUPPOSED TO VERIFY THE LOG THEN?

BEGIN {
  event_template["E1"] = "jk2_init() Found child <*> in scoreboard slot <*>" 
  event_template["E2"] = "workerEnv.init() ok <*>"
  event_template["E3"] = "mod_jk child workerEnv in error state <*>"
  event_template["E4"] = "[client <*>] Directory index forbidden by rule: <*>"
  event_template["E5"] = "jk2_init() Can't find child <*> in scoreboard"
  event_template["E6"] = "mod_jk child init <*> <*>"
}

/jk2_init\(\) Found child [0-9][0-9]* in scoreboard slot [0-9][0-9]*/ {
  print $0 ",E1," event_template["E1"];
}

/workerEnv\.init\(\) ok .*/ {
  print $0 ",E2," event_template["E2"];
}

/mod_jk child workerEnv in error state [0-9][0-9]*/ {
  print $0 ",E3," event_template["E3"];
}

/\[client [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\] Directory index forbidden by rule:/ {
  print $0 ",E4," event_template["E4"];
}

/jk2_init\(\) Can't find child [0-9][0-9]* in scoreboard/ {
  print $0 ",E5," event_template["E5"];
}

/mod_jk child init/ {
  print $0 ",E6," event_template["E6"];
}
