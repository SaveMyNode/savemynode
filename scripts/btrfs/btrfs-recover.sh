#!/bin/bash

# Function to print usage information
function usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -d, --device      Specify the device path"
    echo "  -fp, --file-path  Path of the file/dir to recover"
    echo "  -rp, --recovery-path  Specify the recovery path"
    echo "  -D, --depth  Specify the recovery depth"
    echo "  -h, --help       Display this help message"
}

# Check if the partition is mounted before proceeding
function is_mounted() {
    cmd="$(dirname $0)/mount-check.sh $dev"
    res="$(bash ./$cmd)"
    if [[ ! -z $res ]]; then
        echo "ERROR: Device $dev is mounted at $res. Unmount the device before proceeding."
        exit 1
    fi
}

# Initialize variables
dev=""
file_path=""
recovery_path=""

# Function to validate path
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

# Check if required arguments are provided
# if [[ -z "$dev" || -z "$file_path" || -z "$recovery_path" ]]; then
#     echo "Error: Missing required arguments. Use -h for help." >&2
#     exit 1
# fi

# Perform actions based on the provided arguments
echo "Device: $dev"
echo "File Path: $file_path"
echo "Recovery Path: $recovery_path"

# Sanitize filepath
function sanitize_filepath() {
     # Check is first character is a /, if so ignore it
    if [[ $file_path == /* ]]; then
        file_path=$(echo "$file_path"| cut -c2-)
    fi
    echo ""
    if [[ $file_path == */ ]]; then
        rectype="dir"
        recname="$dirname"
        file_path+=".*"
    else
        rectype="file"
        recname="$filename"
    fi
    echo "Sanitized $file_path"

}

# Makes regex to find files which match.
# Regex inspired from @danthem's script
function cook_regex() { 
    cmd="$(dirname $0)/generate-regex.sh $file_path"
    regex="$(bash ./$cmd)"
}

function dryrun_with_depth_levels() {
    echo $depth
    cmd="$(dirname $0)/dry-run.sh $depth $dev $regex"
    res="$(bash $cmd)"
    echo "$cmd"
}

is_mounted
sanitize_filepath
cook_regex
dryrun_with_depth_levels

echo $res

# Get last directory in path and cut out filepath
# and dir name separately
# dir=$(echo "$file_path" | awk -F"/" '{ print $(NF-1) }')
# file=$(echo "$file_path" | awk -F"/" '{ print $NF }')

# echo "Device: $dev Destination: $dest file: $dir / $file"