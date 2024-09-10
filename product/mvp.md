# Expectations from SaveMyNode

### 1. **Inode Scanning and Mapping**
   - **Inode-Based Recovery**: Ability to scan the entire Btrfs file system and map deleted inodes to potential file paths. This can involve reconstructing metadata and directory trees.
   - **Metadata Integrity Check**: Verify the integrity of inodes and metadata before attempting recovery.
   
### 2. **File Fragmentation Handling**
   - **Handling Fragmented Files**: Since Btrfs supports Copy-on-Write (CoW), files may be fragmented across different extents. The tool should be able to handle and reconstruct fragmented files effectively.
   
### 3. **Efficient Search and Recovery**
   - **Selective Recovery**: Allow users to search for specific files based on file name, inode number, size, or modification date, and recover only selected files instead of the entire partition.
   - **Batch Recovery**: Recover multiple files or entire directories in a single operation.
   
### 4. **Snapshot Awareness**
   - **Snapshot-Aware Recovery**: Detect Btrfs snapshots, which may retain old versions of files even after deletion. The tool should be able to recover files from older snapshots.
   
### 5. **File Content Preview**
   - **Data Preview**: Provide a preview option to allow users to inspect the content of files before recovery. This helps ensure the correct version is being recovered.
   
### 6. **File Type Detection**
   - **Automatic File Type Detection**: Implement a system to detect file types (e.g., text, binary, media) even if file extensions are missing or unknown due to metadata loss. This helps with recovery of files when inode information is limited.
   
### 7. **Comprehensive Logging**
   - **Detailed Logging**: Maintain detailed logs of all recovery operations, including inodes scanned, files found, potential issues, and files successfully restored.
   - **Error Reporting**: Include error logs and detailed reasons for any recovery failures.
   
### 8. **Partition Information and Visualization**
   - **Filesystem Metadata Display**: Show detailed partition and filesystem information, including free/used space, number of inodes, and mount status.
   - **Visual Representation**: A user-friendly graphical or tabular representation of files, their statuses (active/deleted), and the ability to sort or filter this information.
   
### 9. **Data Integrity Verification**
   - **Checksum Verification**: Since Btrfs uses checksums for data integrity, the tool should verify the checksums of recovered files to ensure they haven’t been corrupted.
   - **Recovery Consistency Check**: Before restoring, perform checks to ensure that file fragments or extents are consistent and that there’s a low risk of recovering corrupt files.

### 10. **Support for Special Btrfs Features**
   - **Subvolume and Quota Recovery**: Be aware of Btrfs subvolumes and quotas, and be able to recover files while respecting these structures.
   - **Compression Handling**: Recover files that were compressed using Btrfs’s built-in compression algorithms (zlib, zstd, LZO).
   - **RAID Mode Compatibility**: Handle recovery in RAID-0, RAID-1, RAID-10 configurations (used by Btrfs), ensuring data is reconstructed properly based on the RAID level.
   
### 11. **User-Friendly Interface**
   - **Command-Line Interface (CLI)**: Provide a robust CLI with multiple flags for specifying paths, inodes, and filters (e.g., size, type, date).
   - **Graphical Interface (GUI)**: An optional GUI for easier navigation, partition scanning, and file recovery, suitable for non-expert users.
   - **Progress Indicator**: Show progress bars or other indicators during scanning and recovery to keep the user informed.

### 12. **Performance Optimizations**
   - **Efficient Scanning Algorithms**: Employ efficient scanning algorithms to minimize the time required to search through the file system, especially for large partitions.
   - **Multithreading**: Utilize multithreading or parallelization for faster inode scanning and file recovery.
   
### 13. **Recovery Simulation Mode**
   - **Dry-Run Option**: A "dry-run" mode where users can simulate the recovery process to see what files are recoverable without actually performing any recovery actions.
   
### 14. **File Integrity Comparison**
   - **Backup Comparison**: Allow comparison of recovered files with existing backups (if available) to determine whether a file has been successfully restored to its original state.

### 15. **Cross-Filesystem Support**
   - **Export to Other Filesystems**: Support exporting recovered data to different filesystems (e.g., ext4, NTFS), particularly useful if the user wants to back up or migrate data after recovery.

### 16. **Encrypted Partition Support**
   - **Handle Encrypted Volumes**: If the Btrfs partition was encrypted, the tool should support decryption with the correct keys/passwords before attempting recovery.

### 17. **Automation Capabilities**
   - **Scripting Support**: Allow for scripting or automation to recover files in bulk across multiple partitions or systems, especially in large-scale environments.
   
### 18. **Safety Mechanisms**
   - **Non-Destructive Recovery**: Ensure that the tool performs read-only operations on the partition to avoid damaging the filesystem during the recovery process.
   - **Data Backup Before Recovery**: Suggest or offer to create a backup of the current state of the partition before initiating any recovery attempts.

### 19. **Filesystem Health Check**
   - **Pre-Recovery Health Check**: Run a Btrfs health check implementation before starting any recovery operations to ensure that the partition is in a recoverable state.
   
### 20. **Cross-Platform Compatibility**
   - **OS Compatibility**: Ensure the tool is compatible across major operating systems like Linux distributions (Ubuntu, Fedora, etc.), and possibly other platforms where Btrfs support is available.

These features will provide flexibility and control to the user while ensuring efficient, safe, and reliable data recovery from a Btrfs partition.
