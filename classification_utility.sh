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
   echo "  -c     Output CSV file. Default output.csv"
   echo
}

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

# Get the options
while getopts ":hi:p:c:" option; do
   case $option in
      h) # display Help
         Help
         exit;;
      i) # Enter network interface
         INTERFACE=$OPTARG;;
      p) # Enter csv file with registered ports
         PORTS=$OPTARG;;
      c) # Check for ideal -S
         CSV=$OPTARG;;
      \?) # Invalid option
         echo "Load arguments"
         echo "  Error: Invalid argument"
         echo " "
         Help
         exit;;
   esac
done
echo "Load arguments"
if [[ $INTERFACE == "None" ]]
then
    echo "  ERROR: Enter some network interface in -i"
    exit
fi

if test -f "$CSV"; then
    echo "$CSV - OK"
else
    echo "$CSV - created"
    echo "Application,ID_dependency" > "$CSV"
fi

echo "  OK"

tcpdump -n -i "$INTERFACE" | while read b; do
    echo $b
    r=$(python3 check_dependency.py -t "$b" -c "$CSV" -p "$PORTS"  2>&1)    
    if [[ $r == "False" ]]
    then
        ./classification_utility.py -c "$CSV" -p "$PORTS"    
    fi
done
