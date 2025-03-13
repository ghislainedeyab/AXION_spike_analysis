#!/bin/bash

# assign variables to source and destination directories
if [[ $# -eq 1 ]]
then

        origin=$1
else
        echo "Usage: ./spikesort.sh sourcedirname"
        exit 1
fi

# check if directories are valid
for i in "$@"
do
        if [[ ! -d $i ]]
        then 
                echo "Error $i is not a valid directory"
                exit 1
        fi
done

# check if source directory is empty
if [[ $(ls $origin | wc -w) -eq 0 ]]
then
        echo "Error: $origin  has no files"
        exit 1
fi

# find files with spike list
find $origin -name '*_spike_list.csv' -exec awk '
        BEGIN { FS=OFS=","; elec=0; time=0; }
        {
                if (NR == 1) {
                        for (i=1; i<=NF; i++) {
                                if ($i ~ /Electrode/) {
                                        elec=i;
                                }
                                if ($i ~ /Time/) {
                                        time=i;
                                }
                        }

                        base=substr(FILENAME, 1, length(FILENAME)-25);
                        out=base"_well_list";
                        cmd="mkdir "out;
                        system(cmd);

                }

                if (NR != 1 && $elec ~ /_/) {  
                        well=substr($elec,1,3);
                        base=substr(FILENAME, 1, length(FILENAME)-25);
                        out=base"_well_list";
                        path=out"/"well"spikes.csv";
                        print $elec, $time >> path;
                }
        }' {} \;

./spike_filefinder.sh $origin



