import struct
import sys
import os
import hashlib

# Constants
XFS_SUPERBLOCK_OFFSET = 0
XFS_SUPERBLOCK_SIZE = 512
XFS_DINODE_MAGIC = 0x494E  # 'IN'
XFS_EXTENT_FORMAT = 2  # Extent format

class XFSSuperblock:
    def __init__(self, data):
        self.magicnum = struct.unpack_from(">I", data, 0)[0]
        self.blocksize = struct.unpack_from(">I", data, 4)[0]
        self.dblocks = struct.unpack_from(">Q", data, 8)[0]
        self.icount = struct.unpack_from(">Q", data, 104)[0]
        self.ifree = struct.unpack_from(">Q", data, 112)[0]
        self.inodesize = struct.unpack_from(">H", data, 100)[0]
        self.crc = struct.unpack_from(">I", data, 32)[0]  # CRC for v5
        self.uuid = struct.unpack_from("16s", data, 100)[0]  # UUID for v5

    def is_valid(self):
        return self.magicnum == 0x58465342  # "XFSB"

    def display_info(self):
        print("XFS Superblock Information:")
        print(f"  Block Size: {self.blocksize} bytes")
        print(f"  Inode Size: {self.inodesize} bytes")
        print(f"  Total Data Blocks: {self.dblocks}")
        print(f"  Total Inodes: {self.icount}")
        print(f"  Free Inodes: {self.ifree}")
        print(f"  UUID: {self.uuid.hex()}")

class XFSInode:
    def __init__(self, data):
        self.magic = struct.unpack_from(">H", data, 0)[0]
        self.mode = struct.unpack_from(">H", data, 2)[0]
        self.version = struct.unpack_from(">B", data, 4)[0]
        self.format = struct.unpack_from(">B", data, 5)[0]
        self.nlink = struct.unpack_from(">H", data, 16)[0]
        self.uid = struct.unpack_from(">I", data, 18)[0]
        self.gid = struct.unpack_from(">I", data, 22)[0]
        self.size = struct.unpack_from(">Q", data, 56)[0]

    def is_deleted(self):
        return self.nlink == 0 and self.magic == XFS_DINODE_MAGIC

class XFSFileRecovery:
    def __init__(self, image_path):
        self.image_path = image_path
        self.fd = None
        self.superblock = None
        self.image_size = 0

    def open_image(self):
        self.fd = open(self.image_path, 'rb')
        self.image_size = os.path.getsize(self.image_path)  # Get the image size

    def close_image(self):
        if self.fd:
            self.fd.close()

    def read_superblock(self):
        self.fd.seek(XFS_SUPERBLOCK_OFFSET)
        sb_data = self.fd.read(XFS_SUPERBLOCK_SIZE)
        self.superblock = XFSSuperblock(sb_data)

        if not self.superblock.is_valid():
            print("Not a valid XFS filesystem.")
            sys.exit(1)

        self.superblock.display_info()

    def read_inodes(self):
        inode_start_offset = XFS_SUPERBLOCK_OFFSET + XFS_SUPERBLOCK_SIZE
        inodes_read = 0
        self.fd.seek(inode_start_offset)

        while inodes_read < self.superblock.icount:
            inode_data = self.fd.read(self.superblock.inodesize)
            if not inode_data:
                break

            inode = XFSInode(inode_data)
            
            # Only print non-zero inodes for debugging purposes
            if inode.magic != 0 or inode.format != 0 or inode.size != 0:
                print(f"Inode {inodes_read}: Magic = {hex(inode.magic)}, Format = {inode.format}, Size = {inode.size}")

                # Check for valid inode data format (e.g., extents)
                if inode.format == XFS_EXTENT_FORMAT:  # Example: extent format
                    print(f"Valid data inode found at index {inodes_read}, attempting recovery...")
                    self.recover_file(inode, inode_data)
            
            inodes_read += 1

    def recover_file(self, inode, inode_data):
        print("Recovering file from inode data...")
        extents = self.extract_extents(inode, inode_data)
        if not extents:
            print("No extents found for this inode.")
            return

        recovered_filename = f"recovered_file_{id(inode_data)}.dat"
        with open(recovered_filename, 'wb') as out_file:
            for extent in extents:
                self.read_extent_data(extent, out_file)

        print(f"Recovered file written to {recovered_filename}")
        self.verify_integrity(recovered_filename)

    def extract_extents(self, inode, inode_data):
        """Extract extents from inode data based on inode format."""
        extents = []
        if inode.format == XFS_EXTENT_FORMAT:
            # Example calculation; adjust as per actual format
            num_extents = (len(inode_data) - 60) // 16
            for i in range(num_extents):
                offset = 60 + i * 16
                try:
                    start_block = struct.unpack_from(">Q", inode_data, offset)[0]
                    block_count = struct.unpack_from(">I", inode_data, offset + 8)[0]
                except struct.error as e:
                    print(f"Struct unpacking error: {e}")
                    continue

                # Validation checks for extent values
                if start_block * self.superblock.blocksize >= self.image_size:
                    print(f"Invalid extent found: Start Block = {start_block}, exceeds image size.")
                    continue

                print(f"  Found extent: Start Block = {start_block}, Block Count = {block_count}")
                extents.append((start_block, block_count))
        else:
            print(f"Unknown inode format {inode.format}; skipping...")

        return extents

    def read_extent_data(self, extent, out_file):
        """Read data from an extent and write it to the output file."""
        start_block, block_count = extent
        block_size = self.superblock.blocksize

        # Calculate the starting offset
        offset = start_block * block_size

        # Validate offset before seeking
        if offset >= self.image_size:
            print(f"Error: Attempted to seek to offset {offset}, which is outside the image bounds.")
            return

        print(f"Reading data from offset {offset} for {block_count} blocks of size {block_size}.")

        self.fd.seek(offset)

        for _ in range(block_count):
            data = self.fd.read(block_size)
            if not data:
                break
            out_file.write(data)

    def verify_integrity(self, filename):
        """Verify the integrity of the recovered file by computing its hash."""
        hash_md5 = hashlib.md5()
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        print(f"MD5 hash of {filename}: {hash_md5.hexdigest()}")

    def run(self):
        self.open_image()
        self.read_superblock()
        self.read_inodes()
        self.close_image()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python xfs_recovery.py <xfs_disk_image>")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Disk image {image_path} does not exist.")
        sys.exit(1)

    recovery_tool = XFSFileRecovery(image_path)
    recovery_tool.run()
