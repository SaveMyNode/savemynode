#!/bin/bash

# Returns empty string if the device is not mounted, otherwise returns the mount point

dev=$1
mntfind="$(findmnt $dev)"

if [[ -z "$mntfind" ]]; then
    echo ""
else
    echo "$mntfind" | awk '{print $2}'
fi