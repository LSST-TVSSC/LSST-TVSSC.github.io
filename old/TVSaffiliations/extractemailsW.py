# coding: utf-8
# prints the emails and contact info of members of a group to stdout,
# both primary and secondary members
# to two files names SubgroupNames_<subgroup>.dat and SubgroupEmails_<subgroup>.dat
# run as
# $python extractemailsW.py "Tidal Disruption Events"

from __future__ import print_function
'__author__' == 'Federica Bianco, NYU - GitHub: fedhere'

import pandas as pd
import sys
from argparse import ArgumentParser
from config import tvsfile

sbuglist = ['']


def my_parse_args():
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
                        '-'.join([s for s in subglist]))
    args = parser.parse_args()

    return args


if __name__ == '__main__':

    TVSMembers = pd.read_csv('https://docs.google.com/spreadsheets/d/' +
                             tvsfile +
                             '/export?gid=0&format=csv',
                             index_col=0)

    TVSMembers['last name'] = TVSMembers.index
    
    subgroups = TVSMembers.primary.unique()
    global subglist
    subglist = [x for x in subgroups if str(x) != 'nan']
    conf = my_parse_args()
    primary = conf.subgroup
    secondary = conf.subgroup

    tmp = TVSMembers[TVSMembers.primary == primary]

    sgemails = tmp['email'].values
    femailName = 'SubgroupEmails_' + ''.join(primary.split()).\
                 replace('/', '')+'.dat'
    femail = open(femailName, 'w')
    femail.write("These are the members with primary affiliation with " + 
                 primary + "\n")
    femail.write("\n")
    femail.write('\n'.join([em + ','for em in sgemails]))
    femail.write("\n")

    sgLnames = tmp['last name'].values
    sgFnames = tmp['first name'].values

    fnamesName = 'SubgroupNames_' + ''.join(primary.split()).\
                 replace('/', '') + '.dat'
    fnames = open(fnamesName, 'w')
    fnames.write("These are the members with primary affiliation with " +
                 primary + "\n")
    fnames.write("\n")
    for em in zip(sgLnames, sgFnames, sgemails):
        fnames.write('{0:15} {1:15} {2}\n'.format(em[0], em[1], em[2]))
 

    tmp = TVSMembers[(TVSMembers.secondary == secondary) | (TVSMembers['secondary.1'] == secondary) | (TVSMembers['secondary.2'] == secondary)]

    sgemails = tmp['email'].values
    femail.write("\n")
    femail.write("These are the members with secondary affiliation with " + secondary + "\n")
    femail.write("\n")
    femail.write('\n'.join([em + ','for em in sgemails]))
    
    sgLnames = tmp['last name'].values
    sgFnames = tmp['first name'].values
    sgPrimary = tmp['primary'].values

    fnames.write("\n")
    fnames.write("These are the members with secondary affiliation with " + secondary + " and their primary affiliation\n")
    fnames.write("\n")
    for em in zip(sgLnames, sgFnames, sgemails, sgPrimary):
        fnames.write('{0:15} {1:15} {2:40} {3}\n'.format(em[0], em[1], em[2], em[3]))
    
    print ("output left in " + fnamesName + " and " + femailName)
