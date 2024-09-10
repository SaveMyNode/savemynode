# recovery_operations.py
import subprocess

# @OPERATIONS 
# 
# Currently WIP this is just some boilerplate code 
#

def recover_btrfs(drive):
    try:
        command = f"btrfs restore {drive} /recovered_data"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return f"Btrfs recovery successful: {output.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error during Btrfs recovery: {e.output.decode()}"

def recover_xfs(drive):
    try:
        command = f"xfs_undelete -v {drive} /recovered_data"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return f"XFS recovery successful: {output.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error during XFS recovery: {e.output.decode()}"
