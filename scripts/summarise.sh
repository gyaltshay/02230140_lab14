#!/bin/sh
# Usage: sh scripts/summarise.sh evidence/t5-recreate.log
set -eu
[ "$#" -eq 1 ] && [ -f "$1" ] || { echo 'Usage: summarise.sh LOGFILE' >&2; exit 1; }
# Normalize BOM and CRLF; extract exactly one log line per request.
awk '
{gsub(//, ""); sub(/^ï»¿/, "")}
$2 == "OK" || $2 == "FAIL" {
  count++;
  if (!first) first=$1;
  last=$1;
  if ($2 == "FAIL") failed++;
  if ($2 == "OK" && match($0, /"version":"[^"]+"/)) {
    version=substr($0,RSTART+11,RLENGTH-12);
    seen[version]++;
  }
}
END {
  print "Total requests:", count+0;
  print "Failed requests:", failed+0;
  print "First timestamp:", first;
  print "Last timestamp:", last;
  print "Responses per version:";
  for (v in seen) print "  " v ": " seen[v];
}' "$1"
