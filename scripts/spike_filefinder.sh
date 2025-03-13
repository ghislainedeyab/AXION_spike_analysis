#!/bin/bash

# assign variables to source and destination directories
if [[ $# -eq 1 ]]
then 

	origin=$1
else
	echo "Usage: ./spike_filefinder.sh sourcedirname"
	exit 1
fi

# check if directories are valid
for i in "$@"
do
	if [[ ! -d $i ]]
	then 
		echo "Error!! $i is not a valid directory"
		exit 1
	fi
done


# check if source directory is empty
if [[ $(ls $origin | wc -w) -eq 0 ]]
then
	echo "Error!! $origin  has no files"
	exit 1
fi


# find files with spike list
find $origin -name '*_spikes.csv' -exec python ./spike_raster.py {} \;
