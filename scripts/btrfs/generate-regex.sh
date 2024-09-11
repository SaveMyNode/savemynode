#!/bin/bash

file_path="$1"
# Script to generate regex for the required filepath
IFS='/' read -ra file_patharray <<< "$file_path"
    
if [[ ${#file_patharray[@]} -eq 1 ]]; then
    # No '/' found, user is looking for a file in root of FS itself
    regex="(|${file_patharray[0]})"
else
    # Build the first part of the regex
    regex="(|${file_patharray[0]}"
    
    # Build the regex one segment at a time
    for ((i=1; i<${#file_patharray[@]}; i++)); do
        regex+="(|/${file_patharray[i]}"
    done
    
    # Close all the parentheses
    for ((i=0; i<${#file_patharray[@]}; i++)); do
        regex+=")"
    done
fi
echo $regex