# @TESTING 
# 
# This file is just for unit testing (will be worked upon more in the future)
# 

import unittest
from unittest.mock import patch
from recovery_operations import recover_btrfs, recover_xfs

class TestRecoveryOperations(unittest.TestCase):

    @patch('subprocess.check_output')
    def test_recover_btrfs(self, mock_subproc):
        mock_subproc.return_value = "Btrfs recovery successful"
        result = recover_btrfs("/dev/sda1")
        self.assertEqual(result, "Btrfs recovery successful")
    
    @patch('subprocess.check_output')
    def test_recover_xfs(self, mock_subproc):
        mock_subproc.return_value = "XFS recovery successful"
        result = recover_xfs("/dev/sda1")
        self.assertEqual(result, "XFS recovery successful")

if __name__ == '__main__':
    unittest.main()
