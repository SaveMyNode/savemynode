# SaveMyNode TUI

**SaveMyNode TUI** is a terminal-based user interface (TUI) built using Python's `rich` library. This tool is intended to facilitate file recovery from drives using Btrfs and XFS file systems. While the UI components and the structure of the tool are implemented, this is currently a dummy interface, and the full file recovery integration is pending.

## Features
- **Dynamic Layout**: The UI is divided into different panels (header, drives, status, and footer) which dynamically display information about the drives, filesystem type, and recovery logs.
- **User Input**: Navigate the TUI with simple keyboard inputs for selecting drives, starting recovery, and managing the log.
- **Animated Progress**: When implemented, recovery will display a live progress bar animation using the `rich` library's progress feature.

## Key Bindings
- **s**: Enter filesystem and drive selection mode
- **r**: Start the recovery process
- **c**: Clear the log
- **q**: Quit the application
- **b**: Go back to the previous screen during selection or recovery

## Prerequisites
- Python 3.7 or higher
- Check [requirements](https://github.com/SaveMyNode/savemynode/blob/main/tui/requirements.txt)
- Linux environment (as the application uses `lsblk` to list drives)
- The `lsblk` command-line utility installed (standard on most Linux distributions)

## Running
   ```bash
   git clone https://github.com/SaveMyNode/savemynode.git
   cd tui/
   python tui.py
   ``` 

> [!IMPORTANT]
> 
> This TUI is currently a massive WIP [work-in-progress]
> 
> We are still learning on the python rich library and have to 
> make a lot of optimisations, UI/UX features and obviously the 
> actual backend integration
> 
