# Workflow

## 1. Introduction
SaveMyNode is a file recovery tool designed to retrieve deleted files from Btrfs and XFS file systems. It features a clean GUI with partition details, file system selection, and recovery functionality.

## 2. Application Flow

### Step 1: Introduction Screen
- The app starts with a welcoming screen, providing a brief overview of the SaveMyNode tool.

### Step 2: Filesystem and Drive Selection
- Users are prompted to select the file system (Btrfs or XFS) and the specific drive from which they want to recover files.
- **UI Elements**: 
  - Dropdown to select file system.
  - ComboBox to select available drives.

### Step 3: Partition Details
- After selecting the drive, SaveMyNode displays partition details (size, type, mount point).
- **UI Elements**:
  - Text area showing detailed drive information retrieved using `lsblk`.

### Step 4: File Recovery
- Users can start the file recovery process by clicking the "Start Recovery" button.
- SaveMyNode will then call appropriate recovery functions (`recover_btrfs` or `recover_xfs`) based on the file system selected.

> [!NOTE]
> 
> SaveMyNode is currently a WIP (Work-In-Progress)
> 
> As such, we only have a working model for extraction the 
> **latest** deleted inode from a **BTRFS** based parition ONLY 
> 
> There is still more research and planning need to be done in order to 
> expand the scope of the product

### Step 5: Output
- The recovery logs and result are shown in a text box below the recovery button.

### Animations and Transitions
- Smooth screen transitions using GTK animations.
- Scrolling partition details for a lively user experience.

## 3. Flow of the Idea

### Problem:
Recovering deleted files from complex file systems (Btrfs/XFS) can be daunting without a graphical tool.

### Solution:
SaveMyNode provides an intuitive interface for recovering deleted files by:
1. Abstracting complexity for users.
2. Displaying filesystem and partition details visually.
3. Offering an easy one-click recovery mechanism.
