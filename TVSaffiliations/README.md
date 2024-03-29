# TVSaffiliations

A Google Colab notebook (python langauge) allows anyone with access to extract the most recent list of emails for any TVS subgroup

This functionality is also offered as scripts, but scripts are no longer being maintained

## USE THE NOTEBOOK [TVS_ContactSubgroupMembers.ipynb](https://github.com/LSST-TVSSC/LSST-TVSSC.github.io/blob/master/TVSaffiliations/TVS_ContactSubgroupMembers.ipynb)- OPEN IN COLAB (buttom at the top of the notebook)


Change the value of tvsfile in conf.py to the correct GoogleDoc file link, which the TVS co-chairs Ashish and Federica can provide.

## Without the GUI: 

### to obtain all contact info:
run as

    python extractemailsW.py <subgroup>

this creates (overwrites if existing) 2 output files with the contact info: SubgroupNames_<subgroup>.dat which contains the Last-, First-Name, and email in a tsv file, and SubgroupEmails_<subgroup>.dat, which contains the emails only (for easier copy and paste in your email To field).

to see a list of the subgroups run as   

    python extractemailsW.py  -h

### to just get the emails printed on standard output (i.e. dumped to your terminal - generally)

run as 

    python extractemails_nogui.py <subgroups>

to see a list of the subgroups run as   

    python extractemails_nogui.py  -h


## GUI use:

run as 

    python extractemails.py
  

The GUI will ask you which affiliation you are interested in and a list of emails of member with that primary subgroup affiliation, and a list of emails of member with that secondary subgroup affiliation are printed.

Notice: depending on your python version and your system running the command may return an error related to screen access


    This program needs access to the screen.
    Please run with a Framework build of python, and only when you are
    logged in on the main display of your Mac.

In this case use pythonw

    pythonw exractemails.py


Required modules: 
for nogui version 
        Pandas
for gui version 
        pandas, Gooey, wx


# Additional code:

## Visualizations

submitNewMember.py reads in the headerofa TVS applicationto submit the google form. OBSOLETE since now theform has a reCaptha anddoesnot allow robots anymore

mapTVS.ipny maps the TVS members. Download the LSST google doc to use as input

affiliations.html visualizes the connection between member subgroup applications

