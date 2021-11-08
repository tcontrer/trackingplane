# trackingplane
Simulations and Analysis of possible NEXT Tracking Plane configurations.

Each of these scripts (sipmstudy_*) should include a description of its function. Each script
takes the following arguments (currently set within the code, sorry I want to
  eventually make this an argument in the script):

    nfiles (number of files to to run over)
    local (boolean to state whether running locally or on the cluster)
    event_type (type of event, kr or qbb)
    teflon (boolean to state whether to run with teflon or not)

The local, event_type, and teflon are used to define the input and output paths.
The event_type is also used in the script to set the titles of plots and range.

Each sipmstudy script used open_files.py to read in the files. Edit open_files.py
to change the input and output directory.

The subdirectory test_notebooks includes jupyter notebooks for testing. 
