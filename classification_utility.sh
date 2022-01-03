#!/bin/bash

############################################################
# Help                                                     #
############################################################
Help()
{
   # Display Help
   echo "Usage:"
   echo "  Add description of the script functions here."
   echo
   echo "  Syntax: scriptTemplate [-h | -r ] (-p | -j | -S)"
   echo "  options:"
   echo "  -h     Print this Help."
   echo "  -i     Network interface (mandatory parameter)"
   echo "  -p     Path to CSV file with registered ports. Default Ports.csv"
   echo "  -l     Choose chrowsers lgo files. Supported browser: Chrome, Firefox"
   echo "  -f     Path to Firefox log file"
   echo "  -d     Path to folder Firefox log files"
   echo "  -c     Output CSV file. Default output.csv"
   echo
}

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

############################################################
############################################################
# Main program                                             #
############################################################
############################################################
############################################################
# Process the input options. Add options as needed.        #
############################################################
# Set variables
INTERFACE="None"
PORTS="Ports.csv"
CSV="output.csv" 
SOURCE="None"
# Get the options
while getopts ":hi:p:l:d:f:c:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      i) # Enter network interface
         INTERFACE=$OPTARG;;
      p) # Enter csv file with registered ports
         PORTS=$OPTARG;;
      l) # Enter name of browser to log
         LOG=$OPTARG;;
      d) # Enter csv file with registered ports
         D=$OPTARG
         SOURCE="True";;
      f) # Enter csv file with registered ports
         F=$OPTARG
         SOURCE="False";;
      c) 
         CSV=$OPTARG;;
      \?) # Invalid option
         echo -e "${RED}Load arguments"
         echo "  Error: Invalid argument"
         echo " "
         Help
         exit;;
   esac
done
echo -e "${GREEN}Load arguments"
if [[ $INTERFACE == "None" ]]
then
    echo -e "  ${RED}ERROR: Enter some network interface in -i"
    exit
fi

if test -f "$CSV"; then
    echo -e "  ${GREEN}OK: $CSV"
else
    echo -e "  ${YELLOW}WARNING: $CSV wasn't exists. New file $CSV was created."
    echo "Application,ID_dependency" > "$CSV"
fi
echo -e "${NC}"

tcpdump -n -i "$INTERFACE" | while read b; do
    echo $b
    r=$(python3 check_dependency.py -t "$b" -c "$CSV" -p "$PORTS"  2>&1)    
    if [[ $r == "False" ]]
    then
         ./classification_utility.py -c "$CSV" -p "$PORTS"
         if [[ $LOG == "Firefox" ]]
         then
            if [[ $SOURCE == "False" ]]
            then
                  ./firefox_dns_miner.py -t "$b" -c "$CSV" -p "$PORTS" -f "$F"
            elif [[ $SOURCE == "True" ]] 
            then
                  ./firefox_dns_miner.py -t "$b" -c "$CSV" -p "$PORTS" -d "$D"
            else
               echo -e "  ${RED}ERROR: Firefox log file isn't placed in -f or firefox log folder isn't placed in -d"
               exit
            fi  
         fi
    fi
done

if [[ $LOG == "Chrome" ]]
then
   if [[ $SOURCE == "False" ]]
   then
      ./chrome_log_miner.py -c "$CSV" -p "$PORTS" -f "$F"
   else
      echo -e "  ${RED}ERROR: Chrome log file isn't placed in -f"
      exit
   fi  
fi 
