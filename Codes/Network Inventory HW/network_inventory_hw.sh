#!/usr/bin/env bash
set -e

usage="$(basename "$0") [-h] [-t TYPE] [-f HOSTS] [-s ssh jump (-o -u -p) ] [-d default]
Network Inventory HW
Warning: this code uses CLI command to get primary and secondary image, please use -t if the routers use MD-CLI
where:
EX : - ./network_inventory_hw.sh -t -f /path/to/hosts.txt
     - ./network_inventory_hw.sh -d
     - ./network_inventory_hw.sh -t -f /path/to/hosts.txt -s -o 192.168.1.2 -u myuser -p mypassword
     
    -h !show this help text
    -t !to set CLI Type to Model Driven (by default is cli classic)
    -f  path of text file of hosts (by default hosts.txt)
    -s !to use ssh jump (in this case you need to add -o (host), -u (username) and -p (password)) 
    -d !Run on default
     !  means that it doesn't need a parameter"


ssh_jump="False"
hosts="hosts.txt"
type="True"
while getopts ':htf:so:u:p:d' option; do
  case "$option" in
    h) xxx="True"; echo "$usage"; exit;;
    t) xxx="True"; type="False";;
    f) xxx="True"; hosts=$OPTARG;;
    d) xxx="True";;
    s) xxx="True"; ssh_jump="True";;
    o) hostt=$OPTARG;;
    u) user=$OPTARG;;
    p) pass=$OPTARG;;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done

# Check if mandatory arguments are provided
if [[ -z $xxx ]]; then
  echo "At least one argument must be provided (h, t, f, s or d)"
  echo "$usage" >&2; exit 1
fi

if [[ $ssh_jump == "True" && ( -z $hostt || -z $user || -z $pass ) ]]; then
  echo "You need some ssh jump parameters"
  echo "$usage" >&2; exit 1
fi

command="robot -v CLI:$type -v hosts:$hosts -v ssh_jump:$ssh_jump -v jumphost:$hostt -v jumpuser:$user -v jumppass:$pass ./Network_Inventory_HW.robot"
#printf  "\ncommand = ${command}\n"
eval "$command"
