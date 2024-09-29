#!/bin/bash

# Function to print usage information
function usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -d,  --device           Specify the device path"
    echo "  -fp, --file-path        Path of the file/dir to recover"
    echo "  -rp, --recovery-path    Specify the recovery path"
    echo "  -D,  --depth            Specify the recovery depth"
    echo "  -R,  --recover          If 1, recover the files along with printing logs"
    echo "  -h,  --help             Display this help message"
}

# Check if the partition is mounted before proceeding
# mount-check.sh expects: 
# Argument 1: device path (e.g., /dev/sdb1)
function is_mounted() {
    cmd="$(dirname $0)/mount-check.sh $dev"
    res="$(bash ./$cmd)"
    if [[ ! -z $res ]]; then
        echo "ERROR: Device '$dev' is mounted at '$res'."
        echo "Please unmount the device before proceeding."
        exit 1
    fi
}

# Initialize variables
dev=""
file_path=""
recovery_path=""

# Function to validate the path
validate_path() {
    if [ ! -e "$1" ]; then
        echo "Error: Path '$1' does not exist."
        exit 1
    fi
}

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--device)
            dev="$2"
            validate_path "$dev"
            shift 2
            ;;
        -fp|--file-path)
            file_path="$2"
            shift 2
            ;;
        -rp|--recovery-path)
            recovery_path="$2"
            validate_path "$recovery_path"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -D|--depth)
            depth="$2"
            shift 2
            ;;
        -R|--recover)
            recover="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if required arguments are provided
if [ -z "$dev" ] || [ -z "$file_path" ] || [ -z "$recovery_path" ] || [ -z "$depth" ]; then
    echo "Error: Missing required arguments."
    usage
    exit 1
fi

# Function to sanitize file path
function sanitize_filepath() {
    # If the file path starts with '/', remove it
    if [[ $file_path == /* ]]; then
        file_path=$(echo "$file_path" | cut -c2-)
    fi

    echo ""
    # If the file path ends with '/', assume it's a directory
    if [[ $file_path == */ ]]; then
        rectype="dir"
        recname="$dirname"
        file_path+=".*"  # Append .* for matching all files in the directory
    else
        rectype="file"
        recname="$filename"
    fi

    echo "Sanitized file path: '$file_path'"
}

# Function to generate regex for file recovery
# generate-regex.sh expects:
# Argument 1: sanitized file path to create the regex pattern
function cook_regex() { 
    cmd="$(dirname $0)/generate-regex.sh $file_path"
    regex="$(bash ./$cmd)"
}

# Function for dry-run file recovery with depth levels
# dry-run.sh expects:
# Argument 1: depth (e.g., how deep the recovery should go)
# Argument 2: device path (e.g., /dev/sdb1)
# Argument 3: regex (to find files based on the pattern)
# Optional Argument 4: 1 if recovery should happen, 0 for just logging
# Optional Argument 5: recovery path (where recovered files will be stored)
function dryrun_with_depth_levels() {
    cmd="$(dirname $0)/dry-run.sh $depth $dev $regex"
    res="$(bash $cmd)"
    echo "$cmd"
}

# Function to recover files
# dry-run.sh with recovery option expects:
# Argument 1: depth (how deep to search)
# Argument 2: device path
# Argument 3: regex (generated earlier)
# Argument 4: recovery flag (1 for recovery)
# Argument 5: recovery path (where to save the recovered files)
function recover() { 
    cmd="$(dirname $0)/dry-run.sh  $depth $dev $regex 1 $recovery_path"
    regex="$(bash ./$cmd)"
}

# Check if the device is mounted
is_mounted

# Sanitize file path and generate recovery regex
sanitize_filepath
cook_regex

# Perform dry-run recovery with specified depth
dryrun_with_depth_levels

# If recover flag is set, perform actual file recovery
if [[ $recover -eq 1 ]]; then 
    recover
fi

# Output the result of the operation
echo "$res"
