#!/bin/bash
roots="/tmp/btrfsroots.tmp"
tmp="/tmp/undeleter.tmp"
rectype="none"

depth=$1
dev=$2
regex=$3

# If 1 then recover files to the destination directory
recover=$4
dst=$5

function generateroots(){
  if [[ $depth -eq 1 || $depth -eq 0 ]]; then
    sudo btrfs-find-root "$dev" &> "$tmp"
    grep -a Well "$tmp" | sed -r -e 's/Well block ([0-9]+).*/\1/' | sort -rn > "$roots"
    rootcount=$(wc -l "$roots" | awk '{print $1}')
    > "$tmp"
  elif [[ $depth -eq 2 ]]; then
    sudo btrfs-find-root -a "$dev" &> "$tmp"
    grep -a Well "$tmp" | sed -r -e 's/Well block ([0-9]+).*/\1/' | sort -rn > "$roots"
    rootcount=$(wc -l $roots | awk '{print $1}')
    > "$tmp"
  fi
}

function dryrun(){
  if [[ $depth -eq 0 ]]; then
    sudo btrfs restore -Divv --path-regex '^/'${regex}'$' "$dev" /  2> /dev/null | grep -E "Restoring.*$recname" | cut -d" " -f 2- &> $tmp
    # Level 1 finds roots and loops through them
  elif [[ $depth -eq 1 ]]; then
    while read -r i || [[ -n "$i" ]]; do
      sudo btrfs restore -t "$i" -Divv --path-regex '^/'${regex}'$' "$dev" / 2> /dev/null | grep -E "Restoring.*$recname" | cut -d" " -f 2- &>> $tmp
    done < "$roots"
    # add the -a flag to the btrfs-find-roots, to find more roots
  elif [[ $depth -eq 2 ]]; then
    while read -r i || [[ -n "$i" ]]; do
      sudo btrfs restore -t "$i" -Divv --path-regex '^/'${regex}'$' "$dev" / 2> /dev/null| grep -E "Restoring.*$recname" | cut -d" " -f 2- &>> $tmp
    done < "$roots"
  fi
}

function checkresult(){
    if [[ ! -s $tmp ]]; then 
        echo "No results found"
    else 
        cat $tmp
    fi
}

function recover(){
  if [[ $depth = "0" ]]; then
    sudo btrfs restore -ivv --path-regex '^/'${regex}'$' "$dev" "$dst"  &> /dev/null &
    recoveredfiles=$(find "$dst" ! -empty -type f | wc -l)
  elif [[ $depth == "1" ]]; then
    while read -r i || [[ -n "$i" ]]; do
      sudo btrfs restore -t "$i" -ivv --path-regex '^/'${regex}'$' "$dev" "$dst" &> /dev/null
    done < "$roots" &
    # Find and delete empty files in $dst
    # so that we don't skip recovering a file on next iteration just because an empty version of the same file was recovered
    recoveredfiles=$(find "$dst" ! -empty -type f | wc -l)
  elif [[ $depth == "2" ]]; then
    while read -r i || [[ -n "$i" ]]; do
      sudo btrfs restore -t "$i" -ivv --path-regex '^/'${regex}'$' "$dev" "$dst" &> /dev/null
    done < "$roots" &
    recoveredfiles=$(find "$dst" ! -empty -type f | wc -l)
  fi
}

generateroots
dryrun
checkresult
if [[ $recover -eq 1 ]]; then
    recover
fi
