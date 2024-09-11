import os
import subprocess
from time import sleep
from rich.console import Console, Group
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.live import Live
from rich import box
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.align import Align
import readchar
import time

console = Console()

class SaveMyNodeTUI:
    def __init__(self):
        self.filesystem_type = None
        self.drive_path = None
        self.recovery_path = None
        self.target_directory = None
        self.layout = Layout()
        self.setup_layout()
        self.log_messages = []
        self.current_mode = "main"

    def setup_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="drives", ratio=2),
            Layout(name="status", ratio=1)
        )

    def run(self):
        with Live(self.layout, refresh_per_second=4, screen=True) as live:
            while True:
                self.update_layout()
                live.update(self.layout)

                key = readchar.readkey()
                if self.current_mode == "main":
                    if key == 's':
                        self.current_mode = "select"
                    elif key == 'r':
                        self.current_mode = "recover"
                    elif key == 'c':
                        self.log_messages.clear()
                    elif key == 'q':
                        break
                    else:
                        self.log_messages.append("[red]Invalid command. Use s, r, c, or q.[/red]")
                elif self.current_mode == "select":
                    self.select_filesystem_and_drive(key)
                elif self.current_mode == "recover":
                    self.start_recovery(key)

    def update_layout(self):
        self.layout["header"].update(Panel("SaveMyNode - Inode Recovery Tool", style="bold green"))
        self.layout["main"]["drives"].update(self.get_drives_panel())
        self.layout["main"]["status"].update(self.get_status_panel())
        self.layout["footer"].update(self.get_footer_panel())

    def get_drives(self):
        """Get available drives using lsblk."""
        result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT"], capture_output=True, text=True)
        drives = result.stdout.splitlines()[1:]  # Skip the header
        return drives

    def get_drives_panel(self):
        table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        table.add_column("NAME", style="cyan")
        table.add_column("FSTYPE", style="green")
        table.add_column("SIZE", style="yellow")
        table.add_column("MOUNTPOINT", style="blue")

        result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT"], capture_output=True, text=True)
        for line in result.stdout.splitlines()[1:]:  # Skip the header
            parts = line.split()
            if len(parts) == 4:
                table.add_row(*parts)
            elif len(parts) == 3:
                table.add_row(parts[0], parts[1], parts[2], "")

        return Panel(table, title="Partition Details", border_style="green")

    def get_status_panel(self):
        status = f"""
Filesystem: {self.filesystem_type or 'Not selected'}
Drive: {self.drive_path or 'Not selected'}
Recovery Path: {self.recovery_path or 'Not set'}
Target Directory: {self.target_directory or 'Not set'}

Log:
{"".join(self.log_messages[-5:])}  # Show last 5 log messages
        """
        return Panel(status, title="Status", border_style="blue")

    def get_footer_panel(self):
        if self.current_mode == "main":
            return Panel("s: select filesystem/drive | r: start recovery | c: clear log | q: quit", style="italic")
        elif self.current_mode == "select":
            return Panel("1: Btrfs | 2: XFS | Enter drive number | b: back", style="italic")
        elif self.current_mode == "recover":
            return Panel("Enter recovery path and target directory | b: back", style="italic")

    def floating_prompt(self, message):
        """Create a floating panel prompt"""
        prompt_panel = Panel(
            Align.center(message),
            box=box.ROUNDED,
            padding=(1, 2),
            border_style="magenta",
        )
        self.layout["main"]["drives"].update(Group(self.get_drives_panel(), Align.center(prompt_panel)))

    def select_filesystem_and_drive(self, key):
        if key == 'b':
            self.current_mode = "main"
            return

        if not self.filesystem_type:
            self.floating_prompt("Press 1 for Btrfs or 2 for XFS")
            if key == '1':
                self.filesystem_type = "Btrfs"
            elif key == '2':
                self.filesystem_type = "XFS"
            else:
                self.log_messages.append("[red]Invalid filesystem type.[/red]")
            return

        if key.isdigit():
            drives = self.get_drives()
            drive_index = int(key)
            if 0 <= drive_index < len(drives):
                self.drive_path = drives[drive_index].split()[0]
                self.log_messages.append(f"[green]Selected {self.filesystem_type} filesystem on drive {self.drive_path}[/green]")
                self.current_mode = "main"
            else:
                self.log_messages.append("[red]Invalid drive index.[/red]")
        else:
            self.log_messages.append("[red]Invalid input. Enter the drive number.[/red]")

    def start_recovery(self, key):
        if key == 'b':
            self.current_mode = "main"
            return

        if not self.filesystem_type or not self.drive_path:
            self.log_messages.append("[red]Error: Select filesystem and drive first[/red]")
            self.current_mode = "main"
            return

        if not self.recovery_path:
            self.recovery_path = self.get_user_input("Enter recovery path: ")
            return

        if not self.target_directory:
            self.target_directory = self.get_user_input("Enter target directory: ")
            if not os.path.exists(self.recovery_path) or not os.path.exists(self.target_directory):
                self.log_messages.append("[red]Error: Invalid recovery path or target directory[/red]")
                self.recovery_path = None
                self.target_directory = None
                self.current_mode = "main"
                return

        self.log_messages.append(f"[green]Starting recovery...[/green]")
        self.recovery_animation()

    def recovery_animation(self):
        """Simulate a recovery process with a progress bar."""
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            console=console,  # Pass the existing console object
            transient=True  # Optional: Makes the progress bar disappear when done
        ) as progress:
            task = progress.add_task("[green]Recovering files...", total=100)
            
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.05)  # Simulate recovery progress


    def get_user_input(self, prompt):
        user_input = ""
        while True:
            self.floating_prompt(f"{prompt}{user_input}")
            key = readchar.readkey()
            if key == readchar.key.ENTER:
                return user_input
            elif key == readchar.key.BACKSPACE:
                user_input = user_input[:-1]
            else:
                user_input += key


if __name__ == "__main__":
    SaveMyNodeTUI().run()
