# coding: utf-8
#just prints the emails of members of a group to stdout,
#both primary and secondary members
# run as
# $python extractemails_nogui.py "Tidal Disruption Events"

from __future__ import print_function
'__author__' == 'Federica Bianco, NYU - GitHub: fedhere'
import sys
import pandas as pd
from argparse import ArgumentParser
from config import tvsfile


if __name__ == '__main__':
    if tvsfile is None:
        print ("Required Argument: Google Doc file identifier (if you do not have it email federica!)")
        sys.exit()

    TVSMembers = pd.read_csv('https://docs.google.com/spreadsheets/d/' +
                             tvsfile +
                             '/export?gid=0&format=csv',
                             index_col=0)
    subgroups = TVSMembers.primary.unique()
    TVSMembers.groupby('primary').count().hist()
    

