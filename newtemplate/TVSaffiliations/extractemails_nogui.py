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


def parse_args(subglist):
    """ Use ArgParser to build up the arguments we will use in our script
    """
    stored_args = {}
    # get the script name without the extension & use it to build up
    # the json filename
    parser = ArgumentParser(description='Selecting members by subgroup')
    parser.add_argument('subgroup',
                        action='store',
                        default=None,
                        help='Choose the subgroup affiliation:' +
                        ' -- '.join([s for s in subglist]))

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    if tvsfile is None:
        print ("Required Argument: Google Doc file identifier (if you do not have it email federica!)")
        sys.exit()

    TVSMembers = pd.read_csv('https://docs.google.com/spreadsheets/d/' +
                             tvsfile +
                             '/export?gid=0&format=csv',
                             index_col=0)
    subgroups = TVSMembers.primary.unique()
    conf = parse_args([x for x in subgroups if str(x) != 'nan'])
    primary = conf.subgroup
    secondary = conf.subgroup

    emails = TVSMembers[TVSMembers.primary == primary]['email'].values
    print ("These are the members with primary affiliation with " + primary)
    print ("")
    print (' '.join([em + ','for em in emails]))

    emails = TVSMembers[(TVSMembers.secondary == secondary) | (TVSMembers['secondary.1'] == secondary) | (TVSMembers['secondary.2'] == secondary)]['email'].values
    print ("\n")
    print ("These are the members with secondary affiliation with " + secondary)
    print ("")
    print (' '.join([em + ','for em in emails]))

    print ("")
    print ("If you also want their names and affiliations use: ")
    print ("$python extractemailsW.py " + conf.subgroup)
