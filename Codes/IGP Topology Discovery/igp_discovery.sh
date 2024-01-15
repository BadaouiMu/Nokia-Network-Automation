#!/usr/bin/env bash
set -e

usage="$(basename "$0") [-h] [-f HOSTS] [-s ssh jump (-o -u -p) ] [-d Default]
IGP Topology Discovery
EX : - ./igp_discovery.sh -f /path/to/hosts.txt
     - ./igp_discovery.sh -d
     - ./igp_discovery.sh -s -o 192.168.1.2 -u myuser -p mypassword

    -h !show this help text
    -f  path of text file of hosts (by default hosts.txt)
    -s !to use ssh jump (in this case you need to add -o (host), -u (username) and -p (password)) 
    -d !Run on default
     !  means that it doesn't need a parameter"

HOSTS="hosts.txt"
ssh_jump="False"
while getopts ':hsf:o:u:p:d' option; do
  case "$option" in
    h) xxx="True"; echo "$usage"; exit;;
    f) xxx="True"; HOSTS=$OPTARG;;
    o) hostt=$OPTARG;;
    u) user=$OPTARG;;
    p) pass=$OPTARG;;
    d) xxx="True";;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done

if [[ -z $xxx ]]; then
  echo "At least one argument must be provided (h, t, f, s or d)"
  echo "$usage" >&2; exit 1
fi

COMMAND="robot -v hosts:$HOSTS -v ssh_jump:$ssh_jump -v jumphost:$hostt -v jumpuser:$user -v jumppass:$pass ./IGP_Topology_Discovery.robot"
#printf  "\ncommand = ${COMMAND}\n"
eval "$COMMAND"
