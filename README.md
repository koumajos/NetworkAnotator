# NetworkAnotator

Anotator of network traffic

## Classification utility

This utility that can be run with `sudo bash classification_utility.sh -i <network interface> -c <output csv> -p <ports csv file>` mine information from command `lsof -n -i -P` and safe them to csv file `<output csv>`.

## Firefox log file

In firefox can be setted creating log file for DNS lookups by `about:networking#logging` in firefox search box. And fill the logging as like in picture:

![firefox logs](data/firefox_log.png)

Then before clicking on `Start Logging` go to `DNS` and by clicking on `Clear DNS Cache` clear records. Then go back to `Logging` and click on `Start Logging`.

Firefox will loggg DNS lookups to some file in folder `/tmp/` that starts with `log.txt`.

Then we can mine information about network traffic from this logging file and safe it to some csv file.

Test jupyter notebook for this function is `firefox_log_miner.ipynb`
