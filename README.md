## timecounter
 Cmd line software for tracking your working time

## Getting started

You have to install some python packages by ``` pip install -r requirements.txt```

Then you should init your database by running ``` python log.py --init 1```

To track your activity you should run ``` python log.py --action start ``` or ``` python log.py --action end ``` to start and end your working time correspondenly.

To get analitic for your working time you should run ``` python log.py ```. In default we group your working time by each day, but you can change it for week or month using ```aggregation``` flag.

To get more description of all features run ```python log.py -h```


Congragulations! Now you can track your working time!
