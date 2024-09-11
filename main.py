import gi
import os
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import re

class SaveMyNodeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SaveMyNode - File Recovery Tool")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        # Apply custom CSS
        self.apply_theme()

        # Create a header bar with clickable title
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        self.set_titlebar(header_bar)

        # Create an EventBox to make the label clickable
        title_eventbox = Gtk.EventBox()
        title_label = Gtk.Label(label="SaveMyNode - File Recovery Tool")
        title_label.set_selectable(False)
        title_label.set_name("title_label")
        title_eventbox.add(title_label)
        title_eventbox.connect("button-press-event", self.on_title_clicked)
        header_bar.set_custom_title(title_eventbox)

        # Stack for switching between different views
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        # Add initial recovery screen to the stack
        self.recovery_screen = self.create_recovery_screen()
        self.stack.add_named(self.recovery_screen, "recovery")

        # Placeholder for statistics screen
        self.stats_screen = self.create_statistics_screen()
        self.stack.add_named(self.stats_screen, "statistics")

        # Create a stack switcher to toggle between screens
        stack_switcher = Gtk.StackSwitcher()
        stack_switcher.set_stack(self.stack)
        header_bar.pack_end(stack_switcher)

        self.add(self.stack)

    def apply_theme(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_recovery_screen(self):
        """Creates the initial screen for file recovery."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        self.create_selection_section(box)
        self.create_details_section(box)
        self.create_controls_section(box)

        return box

    def create_statistics_screen(self):
        """Creates the screen to show drive statistics after recovery is selected."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Back button to go back to recovery screen
        back_button = Gtk.Button(label="Back")
        back_button.set_halign(Gtk.Align.START)
        back_button.connect("clicked", self.on_back_button_clicked)
        box.pack_start(back_button, False, False, 10)


        # Create a section for showing statistics
        self.stats_frame = Gtk.Frame(label="Drive Statistics")
        box.pack_start(self.stats_frame, True, True, 10)

        self.stats_textview = Gtk.TextView()
        self.stats_textview.set_editable(False)
        self.stats_textview.set_cursor_visible(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.stats_textview)
        self.stats_frame.add(scrolled_window)

        # Recovery buttons
        self.create_recovery_options(box)

        return box
    
    def create_selection_section(self, parent_box):
        frame = Gtk.Frame(label="Select Filesystem and Drive")
        parent_box.pack_start(frame, False, False, 10)

        # Main horizontal box
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        frame.add(main_box)

        # Box for selection widgets
        selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        main_box.pack_start(selection_box, True, True, 0)

        filesystem_label = Gtk.Label(label="Filesystem:")
        selection_box.pack_start(filesystem_label, False, False, 0)

        self.filesystem_combo = Gtk.ComboBoxText()
        self.filesystem_combo.append_text("BTRFS")
        self.filesystem_combo.append_text("XFS")
        selection_box.pack_start(self.filesystem_combo, False, False, 0)

        drive_label = Gtk.Label(label="Drive:")
        selection_box.pack_start(drive_label, False, False, 0)

        self.drive_combo = Gtk.ComboBoxText()
        self.populate_drive_combo()
        selection_box.pack_start(self.drive_combo, False, False, 0)

        # Create a spacer box
        spacer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        spacer_box.set_hexpand(True)
        main_box.pack_start(spacer_box, True, True, 0)

        # Create the Clear button
        clear_button = Gtk.Button(label="Clear All")
        clear_button.connect("clicked", self.on_clear_button_clicked)
        main_box.pack_end(clear_button, False, False, 10)

    def on_clear_button_clicked(self, widget):
        # Clear filesystem combo box
        self.filesystem_combo.set_active(-1)
        
        # Clear drive combo box
        self.drive_combo.set_active(-1)



    def populate_drive_combo(self):
        try:
            result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT", "--noheadings"], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                for line in output.splitlines()[1:]:
                    self.drive_combo.append_text(line.strip())
        except Exception as e:
            self.show_error_message(f"Error populating drives: {e}")

    def create_details_section(self, parent_box):
        frame = Gtk.Frame(label="Partition Details")
        parent_box.pack_start(frame, True, True, 10)

        self.details_textview = Gtk.TextView()
        self.details_textview.set_editable(False)
        self.details_textview.set_cursor_visible(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.details_textview)
        frame.add(scrolled_window)

        self.refresh_partition_details()

    def refresh_partition_details(self, widget=None):
        try:
            result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT", "--noheadings"], capture_output=True, text=True)
            if result.returncode == 0:
                buffer = self.details_textview.get_buffer()
                buffer.set_text(result.stdout)
            else:
                self.show_error_message("Unable to retrieve partition details")
        except Exception as e:
            self.show_error_message(f"Error: {e}")

    def create_controls_section(self, parent_box):
        button_box = Gtk.Box(spacing=10)
        parent_box.pack_start(button_box, False, False, 10)

        self.start_button = Gtk.Button(label="Start Recovery")
        self.start_button.connect("clicked", self.on_start_recovery_clicked)
        button_box.pack_start(self.start_button, False, False, 0)

        refresh_button = Gtk.Button(label="Refresh Partition Details")
        refresh_button.connect("clicked", self.refresh_partition_details)
        button_box.pack_start(refresh_button, False, False, 0)

    def create_recovery_options(self, parent_box):
        """Creates the buttons for recovery options on the statistics screen."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        parent_box.pack_start(button_box, False, False, 10)

        inode_recovery_button = Gtk.Button(label="Recover Latest Inode")
        inode_recovery_button.connect("clicked", self.on_inode_recovery_clicked)
        button_box.pack_start(inode_recovery_button, False, False, 0)

        partition_recovery_button = Gtk.Button(label="Partition Recovery")
        partition_recovery_button.connect("clicked", self.on_partition_recovery_clicked)
        button_box.pack_start(partition_recovery_button, False, False, 0)

        partition_recovery_button = Gtk.Button(label="Dry Run")
        pattern = ".*"
        command = f'./btrfs-recover.sh -d /dev/nvme0n1p7 -fp "{pattern}" -rp /tmp -D 2'
        partition_recovery_button.connect("clicked", lambda w: self.dry_run(command))
        button_box.pack_start(partition_recovery_button, False, False, 0)

    def show_error_message(self, error_message):
        """Displays a floating window with an error message."""
        dialog = Gtk.Dialog(title="Error", transient_for=self, modal=True)
        dialog.set_default_size(400, 200)

        error_label = Gtk.Label(label=error_message)
        error_label.set_name("error_label")

        # Add error message to the dialog content area
        dialog.get_content_area().pack_start(error_label, True, True, 10)

        # Add a close button
        close_button = dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        close_button.connect("clicked", lambda _: dialog.destroy())

        dialog.show_all()

    def on_title_clicked(self, widget, event):
        self.show_manual()

    def show_manual(self):
        dialog = Gtk.Dialog(title="Manual - SaveMyNode", transient_for=self, modal=True)
        dialog.set_default_size(600, 400)

        # Create a text view for the manual
        manual_textview = Gtk.TextView()
        manual_textview.set_wrap_mode(Gtk.WrapMode.WORD) 
        manual_textview.set_editable(False)
        manual_textview.set_cursor_visible(False)
        manual_textview.get_buffer().set_text(
         "                       SaveMyNode Manual\n\n"
            "1. Select Filesystem and Drive:\n"
            "   - Choose the filesystem type (BTRFS or XFS) from the dropdown.\n"
            "   - Select the drive from the dropdown list.\n\n"
            "2. Partition Details:\n"
            "   - This section displays the details of the partitions on the selected drive.\n\n"
            "3. File Recovery:\n"
            "   - Specify the recovery path where files will be recovered from.\n"
            "   - Specify the target directory where files will be recovered to.\n"
            "   - Click 'Choose' buttons to select directories using a file chooser dialog.\n\n"
            "4. Start Recovery:\n"
            "   - Click 'Start Recovery' to begin the recovery process.\n\n"
            "5. Refresh Partition Details:\n"
            "   - Any changes to the partition table will be reflected."
        )

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.add(manual_textview)
        dialog.get_content_area().add(scrolled_window)

        close_button = dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        close_button.connect("clicked", lambda _: dialog.destroy())

        dialog.show_all()

    def on_back_button_clicked(self, button):
        self.set_title("SaveMyNode - File Recovery Tool")
        self.stack.set_visible_child_name("recovery")

    def on_start_recovery_clicked(self, button):
        filesystem_text = self.filesystem_combo.get_active_text()
        drive_text = self.drive_combo.get_active_text()

        if not filesystem_text or not drive_text:
            self.show_error_message("Please select both filesystem and drive.")
            return

        # Switch to the statistics screen
        self.set_title(f"Recovering from {filesystem_text} ({drive_text})")
        self.stack.set_visible_child_name("statistics")
        self.update_stats_screen(drive_text)


    def update_stats_screen(self, drive_text):
        # Initialize a list to store cleaned drive information
        clean_drive_text = []
        filesystem_text = self.filesystem_combo.get_active_text()
        
        # Extract and clean drive information from drive_text
        drive_names = []
        for line in drive_text.splitlines():
            # Strip leading non-alphabetic characters until the first alphabetic character
            clean_line = re.sub(r'^[^a-zA-Z]+', '', line).strip()
            
            # Split the line and check if it contains necessary parts
            parts = clean_line.split()
            if len(parts) > 2:
                device_name = parts[0]
                device_size = parts[2]
                
                # Check if the size is empty or null
                if not device_size:
                    device_size = "Size information unavailable"
                
                # Add cleaned drive information to the list
                clean_drive_text.append(f"/dev/{device_name} ({device_size})")
                drive_names.append(f"/dev/{device_name}")

        # Join the cleaned drive text into a single string with new lines
        driver_details = "\n".join(clean_drive_text)
        
        # Initialize space variables
        total_space = "N/A"
        used_space = "N/A"
        free_space = "N/A"
        
        # Fetch space details for each drive using lsblk
        for drive_name in drive_names:
            try:
                # Get total size of the drive
                result = subprocess.run(["lsblk", "-b", "-o", "NAME,SIZE", "--noheadings", drive_name], capture_output=True, text=True)
                if result.returncode == 0:
                    size_info = result.stdout.strip().split()
                    if len(size_info) == 2:
                        total_space = size_info[1]
                
                # Get used and free space for the drive
                result = subprocess.run(["df", "-h", drive_name], capture_output=True, text=True)
                if result.returncode == 0:
                    df_output = result.stdout.splitlines()
                    if len(df_output) > 1:
                        usage_info = df_output[1].split()
                        if len(usage_info) >= 4:
                            used_space = usage_info[2]
                            free_space = usage_info[3]

            except Exception as e:
                self.show_error_message(f"Error retrieving drive statistics: {e}")

        # Update the statistics screen with the collected data
        buffer = self.stats_textview.get_buffer()
        buffer.set_text(f"Recovering in {filesystem_text} mode:\n\n"
                         f"Total Space: {total_space}\n"
                         f"Used: {used_space}\n"
                         f"Free: {free_space}\n\n"
                         f"Drive Details:\n{driver_details}")

    def on_inode_recovery_clicked(self, button):
        self.show_recovery_dialog("Inode Recovery", "Enter details for Inode Recovery")

    def on_partition_recovery_clicked(self, button):
        self.show_recovery_dialog("Partition Recovery", "Enter details for Partition Recovery")

    def show_recovery_dialog(self, title, action_desc):
        dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
        dialog.set_default_size(400, 300)

        # Create a VBox to hold the form fields
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        dialog.get_content_area().pack_start(vbox, True, True, 10)

        # Description Label
        description_label = Gtk.Label(label=action_desc)
        vbox.pack_start(description_label, False, False, 0)

        # File Path Entry
        file_path_label = Gtk.Label(label="Restoration Path: *")
        vbox.pack_start(file_path_label, False, False, 0)
        file_path_entry = Gtk.Entry()
        file_path_entry.set_placeholder_text("e.g., /path/to/restore")
        file_path_entry.set_margin_bottom(5)
        vbox.pack_start(file_path_entry, False, False, 0)

        # Filename Entry
        filename_label = Gtk.Label(label="Filename: *")
        vbox.pack_start(filename_label, False, False, 0)
        filename_entry = Gtk.Entry()
        filename_entry.set_placeholder_text("e.g., recovered_file.txt")
        filename_entry.set_margin_bottom(5)
        vbox.pack_start(filename_entry, False, False, 0)

        # Metadata (Date, Time)
        date_label = Gtk.Label(label="Date (YYYY-MM-DD):")
        vbox.pack_start(date_label, False, False, 0)
        date_entry = Gtk.Entry()
        date_entry.set_placeholder_text("e.g., 2024-09-10")
        date_entry.set_margin_bottom(5)
        vbox.pack_start(date_entry, False, False, 0)

        time_label = Gtk.Label(label="Time (HH:MM:SS):")
        vbox.pack_start(time_label, False, False, 0)
        time_entry = Gtk.Entry()
        time_entry.set_placeholder_text("e.g., 14:30:00")
        time_entry.set_margin_bottom(5)
        vbox.pack_start(time_entry, False, False, 0)

        # Buttons
        button_box = Gtk.Box(spacing=10)
        dialog.get_action_area().pack_start(button_box, True, True, 0)
        button_box.set_halign(Gtk.Align.CENTER)

        # Add OK and Cancel buttons
        ok_button = Gtk.Button.new_with_label("OK")
        ok_button.connect("clicked", lambda w: self.on_dialog_response(dialog, file_path_entry, filename_entry, date_entry, time_entry))
        button_box.pack_start(ok_button, True, True, 0)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", lambda w: dialog.destroy())
        button_box.pack_start(cancel_button, True, True, 0)

        dialog.show_all()

    def on_dialog_response(self, dialog, file_path_entry, filename_entry, date_entry, time_entry):
        file_path = file_path_entry.get_text().strip()
        filename = filename_entry.get_text().strip()
        date = date_entry.get_text().strip()
        time = time_entry.get_text().strip()

        # Validate input values
        if not file_path:
            self.show_error_message("Restoration Path cannot be empty.")
            return
        if not filename:
            self.show_error_message("Filename cannot be empty.")
            return 

        # Process the input values
        print(f"Restoration Path: {file_path}")
        print(f"Filename: {filename}")
        print(f"Date: {date}")
        print(f"Time: {time}")

        # Close the dialog
        dialog.destroy()

        # Add actual recovery logic here based on the collected inputs

    def show_error_message(self, error_message):
        """Displays a floating window with an error message."""
        dialog = Gtk.Dialog(title="Error", transient_for=self, modal=True)
        dialog.set_default_size(300, 150)

        error_label = Gtk.Label(label=error_message)
        error_label.set_name("error_label")

        # Add error message to the dialog content area
        dialog.get_content_area().pack_start(error_label, True, True, 10)

        # Add a close button
        close_button = dialog.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        close_button.connect("clicked", lambda _: dialog.destroy())

        dialog.show_all()

    def is_valid_date(self, date_str):
        """Check if the date is in YYYY-MM-DD format."""
        try:
            year, month, day = map(int, date_str.split('-'))
            return 1 <= month <= 12 and 1 <= day <= 31
        except (ValueError, TypeError):
            return False

    def is_valid_time(self, time_str):
        """Check if the time is in HH:MM:SS format."""
        try:
            hour, minute, second = map(int, time_str.split(':'))
            return 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60
        except (ValueError, TypeError):
            return False


    def dry_run(self, command):
        # Create a new top-level window for the dry run
        dialog = Gtk.Window(title="Dry Run Output")
        dialog.set_default_size(600, 400)
        dialog.set_position(Gtk.WindowPosition.CENTER)

        # Create a vertical box to contain the widgets
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dialog.add(vbox)

        # Create a label for the title
        title_label = Gtk.Label(label="Command Output:")
        vbox.pack_start(title_label, False, False, 6)

        # Create a scrolled window to contain the text view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        vbox.pack_start(scrolled_window, True, True, 0)

        # Create a text view to display the command output
        text_view = Gtk.TextView()
        text_view.set_editable(False)  # Make the text view read-only
        scrolled_window.add(text_view)

        # Prefix the command with pkexec to handle sudo permissions
        current_dir = os.getcwd()
        target_dir = "scripts/btrfs/"

        # Change to the target directory if not already in it
        if current_dir != os.path.abspath(target_dir):
            try:
                os.chdir(target_dir)
            except FileNotFoundError as e:
                # Show an error dialog if the directory does not exist
                error_dialog = Gtk.MessageDialog(
                    parent=dialog,
                    flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    message_format=f"Directory error: {e}"
                )
                error_dialog.run()
                error_dialog.destroy()
                return
        full_command = f"pkexec {command}"

        # Run the command and capture the output
        
        try:
            process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if stdout:
                # Create a success dialog for command output
                output_dialog = Gtk.MessageDialog(
                    parent=dialog,
                    flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    message_format="Command Output:"
                )
                output_dialog.format_secondary_text(stdout)
                output_dialog.run()
                output_dialog.destroy()

            if stderr:
                # Create an error dialog for errors
                error_dialog = Gtk.MessageDialog(
                    parent=dialog,
                    flags=Gtk.DialogFlags.MODAL,
                    type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    message_format="Errors:"
                )
                error_dialog.format_secondary_text(stderr)
                error_dialog.run()
                error_dialog.destroy()


        except Exception as e:
            # Create a message dialog for errors
            error_dialog = Gtk.MessageDialog(
                parent=dialog,
                flags=Gtk.DialogFlags.MODAL,
                type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                message_format=f"Error executing command: {e}"
            )
            error_dialog.run()
            error_dialog.destroy()

        # Create a close button
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", lambda w: dialog.destroy())
        vbox.pack_start(close_button, False, False, 6)

        # Show all widgets in the window
        dialog.show_all()
        os.chdir("../..") # quite redundant but words



    def on_exit_clicked(self, button):
        Gtk.main_quit()

if __name__ == "__main__":
    win = SaveMyNodeApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
