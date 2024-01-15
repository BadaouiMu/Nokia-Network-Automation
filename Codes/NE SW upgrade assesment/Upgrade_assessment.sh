#!/usr/bin/env bash
set -e

usage="$(basename "$0") [-h] [-f FILE] [-c Chapitre] [-t HOSTS] [-e excel] [-x excel path] [-s ssh jump (-o -u -p) ] [-d Default]
Network Inventory HW
EX: - ./Upgrade_assessment.sh -e True -x /path/to/excel.xlsx -f /path/to/pdf.pdf -c 'Release 22.2.R1 Supported Hardware'
    - ./Upgrade_assessment.sh  -f /path/to/pdf.pdf -c 'Release 22.2.R1 Supported Hardware' -t /path/to/hosts.txt
    - ./Upgrade_assessment.sh -d
    - ./Upgrade_assessment.sh -t /path/to/hosts.txt -s -o 192.168.1.2 -u myuser -p mypassword

    -h !show this help text
    -f  to specify path of pdf (default 'software.pdf')
    -c  to specify chapitre name (default 'Release 22.2.R1 Supported Hardware')
    -t  to specify host text file (default 'hosts.txt')
    -e !to choose to work with excel instead of hosts.txt (default 'false')
    -x  to specify excel path (default 'Card_Inventory_sample.xlsx')
    -s !to use ssh jump (in this case you need to add -o (host), -u (username) and -p (password)) 
    -d !Run on default
     !  means that it doesn't need a parameter"

EXPATH="Card_Inventory_sample.xlsx"
CHAPITRE="Release 22.2.R1 Supported Hardware"
EXCEL="False"
HOSTS="hosts.txt"
PATH="software.pdf"
ssh_jump="False"

while getopts ':hf:c:t:esx:o:u:p:d' option; do
  case "$option" in
    h) xxx="True"; echo "$usage"; exit;;
    f) xxx="True"; PATH=$OPTARG;;
    c) xxx="True"; CHAPITRE=$OPTARG;;
    t) xxx="True"; HOSTS=$OPTARG;;
    e) xxx="True"; EXCEL="True";;
    x) xxx="True";EXPATH=$OPTARG;;
    o) hostt=$OPTARG;;
    u) user=$OPTARG;;
    p) pass=$OPTARG;;
    d) xxx="True";;
    :) printf "missing argument for -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
   \?) printf "illegal option: -%s\n" "$OPTARG" >&2; echo "$usage" >&2; exit 1;;
  esac
done

# Check if mandatory arguments are provided
if [[ -z $xxx ]]; then
  echo "At least one argument must be provided (h, t, f, s or d)"
  echo "$usage" >&2; exit 1
fi

COMMAND="/home/sats/venvs/sats/bin/robot -v path:$PATH -v hosts:$HOSTS -v excel:$EXCEL -v excel_path:$EXPATH -v ssh_jump:$ssh_jump -v jumphost:$hostt -v jumpuser:$user -v jumppass:$pass ./NE_SW_upgrade_assesment.robot"
printf  "\ncommand = ${COMMAND}\n"
eval "$COMMAND"
