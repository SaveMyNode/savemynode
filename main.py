import gi
import os
import cairo
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import re

class SaveMyNodeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SaveMyNode - File Recovery Tool")
        self.stats_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
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

    def on_draw_partitions(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()

        # Example of updated partition data (you should use actual data here)
        partitions = [
            {"name": "/dev/sda1", "size": 600, "used": 200, "color": (0.3, 0.7, 0.3)},
            {"name": "/dev/sda2", "size": 800, "used": 400, "color": (0.3, 0.3, 0.7)},
            {"name": "/dev/sda3", "size": 1200, "used": 600, "color": (0.7, 0.3, 0.3)}
        ]

        total_size = sum(p["size"] for p in partitions)

        # Draw partitions
        x = 0
        for partition in partitions:
            partition_width = (partition["size"] / total_size) * width
            used_width = (partition["used"] / partition["size"]) * partition_width

            # Draw used space
            cr.set_source_rgb(*partition["color"])
            cr.rectangle(x, 0, used_width, height)
            cr.fill()

            # Draw unused space
            cr.set_source_rgb(0.9, 0.9, 0.9)  # Light gray for unused space
            cr.rectangle(x + used_width, 0, partition_width - used_width, height)
            cr.fill()

            # Draw partition border
            cr.set_source_rgb(0, 0, 0)
            cr.rectangle(x, 0, partition_width, height)
            cr.stroke()

            # Draw partition name
            cr.set_source_rgb(0, 0, 0)
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(12)
            
            name = partition["name"]
            while cr.text_extents(name)[2] > partition_width and len(name) > 3:
                name = name[:-1]
            
            text_x = x + (partition_width - cr.text_extents(name)[2]) / 2
            text_y = height / 2 + cr.text_extents(name)[3] / 2
            cr.move_to(text_x, text_y)
            cr.show_text(name)

            # Draw size information
            size_text = f"{partition['size']}MB"
            used_text = f"{partition['used']}MB used"
            cr.set_font_size(10)
            cr.move_to(x + 5, height - 25)
            cr.show_text(size_text)
            cr.move_to(x + 5, height - 10)
            cr.show_text(used_text)

            x += partition_width

        return False

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

    # def create_details_section(self, parent_box):
    #     frame = Gtk.Frame(label="Partition Details")
    #     parent_box.pack_start(frame, True, True, 10)
    #
    #     vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    #     frame.add(vbox)
    #
    #     self.partition_drawing = Gtk.DrawingArea()
    #     self.partition_drawing.set_size_request(-1, 100)  # Increased height for better visibility
    #     self.partition_drawing.connect("draw", self.on_draw_partitions)
    #     vbox.pack_start(self.partition_drawing, False, False, 0)
    #
    #     self.details_treeview = Gtk.TreeView()
    #     self.create_columns()
    #     self.details_treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
    #
    #     scrolled_window = Gtk.ScrolledWindow()
    #     scrolled_window.set_vexpand(True)
    #     scrolled_window.add(self.details_treeview)
    #     vbox.pack_start(scrolled_window, True, True, 0)
    #
    #     self.details_textview = Gtk.TextView()
    #     self.details_textview.set_editable(False)
    #     self.details_textview.set_cursor_visible(False)

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

    def create_columns(self):
        columns = [
            ("Partition", 0),
            ("File System", 1),
            ("Label", 2),
            ("Size", 3),
            ("Used", 4),
            ("Unused", 5),
            ("Flags", 6)
        ]

        for title, column_id in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=column_id)
            column.set_resizable(True)
            column.set_sort_column_id(column_id)
            self.details_treeview.append_column(column)

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
        restore_path = "/tmp"
        depth = "2";
        dry_run_command = f'./dry-run.sh {depth} /dev/nvme0n1p7 {pattern} 0 {restore_path}'
        partition_recovery_button.connect("clicked", lambda w: self.dry_run(dry_run_command))
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

        # Create the main layout using Gtk.Grid for a well-organized structure
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_border_width(10)

        # Recovery statistics label and text area
        stats_label = Gtk.Label(label="Recovery Statistics", halign=Gtk.Align.START)
        grid.attach(stats_label, 0, 0, 1, 1)

        buffer = self.stats_textview.get_buffer()
        buffer.set_text(f"Recovering in {filesystem_text} mode:\n\n"
                        f"Total Space: {total_space}\n"
                        f"Used: {used_space}\n"
                        f"Free: {free_space}\n\n"
                        f"Drive Details:\n{driver_details}")
        stats_view = Gtk.TextView(buffer=buffer)
        stats_view.set_editable(False)
        stats_view.set_wrap_mode(Gtk.WrapMode.WORD)
        grid.attach(stats_view, 0, 1, 2, 1)

        # File type selection section
        file_types_label = Gtk.Label(label="Select file types:", halign=Gtk.Align.START)
        grid.attach(file_types_label, 0, 2, 1, 1)

        file_types = ["Text Files (.txt)", "Images (.jpg, .png)", "Documents (.pdf, .docx)", 
                      "Audio Files (.mp3, .wav)", "Videos (.mp4, .avi)", "Archives (.zip, .tar)"]

        file_types_text = ", ".join(file_types)  # Join file types as a comma-separated string
        file_types_display_label = Gtk.Label(label=f"File types: {file_types_text}", halign=Gtk.Align.START)
        grid.attach(file_types_display_label, 0, 3, 2, 1)

        confirm_button = Gtk.Button(label="Start Recovery")
        confirm_button.connect("clicked", self.on_confirm_recovery)
        grid.attach(confirm_button, 0, 4, 1, 1)

        # Clear any existing children in the stats container and add the new grid
        for child in self.stats_container.get_children():
            self.stats_container.remove(child)
        
        self.stats_container.pack_start(grid, True, True, 10)
        self.stats_container.show_all()

    def on_confirm_recovery(self, button):
        selected_file_types = [checkbox.get_label() for checkbox in self.file_type_checkboxes if checkbox.get_active()]
        
        if not selected_file_types:
            self.show_error_message("Please select at least one file type.")
            return

        # Here you can add your recovery logic using the selected file types
        print(f"Selected file types: {', '.join(selected_file_types)}")
        self.show_success_message("Recovery started successfully!")

    def on_inode_recovery_clicked(self, button):
        self.show_recovery_dialog("Inode Recovery", "Enter details for Inode Recovery")

    def on_partition_recovery_clicked(self, button):
        # Step 1: Show file chooser dialog for restoration path
        file_chooser = Gtk.FileChooserDialog(
            title="Select Restoration Path",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        file_chooser.set_modal(True)

        response = file_chooser.run()

        if response == Gtk.ResponseType.OK:
            restoration_path = file_chooser.get_filename()
            file_chooser.destroy()

            # Step 2: Show recovery dialog for selecting file types
            self.show_recovery_dialog("Partition Recovery", "Select file types and proceed", restoration_path)
        else:
            file_chooser.destroy()

    def show_recovery_dialog(self, title, action_desc, restoration_path):
        dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
        dialog.set_default_size(400, 300)

        # Create a VBox to hold the form fields
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        dialog.get_content_area().pack_start(vbox, True, True, 10)

        # Description Label
        description_label = Gtk.Label(label=action_desc)
        vbox.pack_start(description_label, False, False, 0)

        # Show the selected restoration path
        restoration_path_label = Gtk.Label(label=f"Restoration Path: {restoration_path}")
        vbox.pack_start(restoration_path_label, False, False, 0)

        # File Types (checkboxes)
        file_types_label = Gtk.Label(label="Select file types:")
        vbox.pack_start(file_types_label, False, False, 0)

        file_types_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.pack_start(file_types_box, False, False, 0)

        # Common file types (all selected by default)
        file_types = ["Text Files (.txt)", "Images (.jpg, .png)", "Documents (.pdf, .docx)", 
                      "Audio Files (.mp3, .wav)", "Videos (.mp4, .avi)", "Archives (.zip, .tar)"]
        file_type_checkboxes = []
        
        for file_type in file_types:
            checkbox = Gtk.CheckButton(label=file_type)
            checkbox.set_active(True)  # All selected by default
            file_type_checkboxes.append(checkbox)
            file_types_box.pack_start(checkbox, False, False, 0)

        # Buttons
        button_box = Gtk.Box(spacing=10)
        dialog.get_action_area().pack_start(button_box, True, True, 0)
        button_box.set_halign(Gtk.Align.CENTER)

        # Add OK and Cancel buttons
        ok_button = Gtk.Button.new_with_label("OK")
        ok_button.connect("clicked", lambda w: self.on_dialog_response(dialog, restoration_path, file_type_checkboxes))
        button_box.pack_start(ok_button, True, True, 0)

        cancel_button = Gtk.Button.new_with_label("Cancel")
        cancel_button.connect("clicked", lambda w: dialog.destroy())
        button_box.pack_start(cancel_button, True, True, 0)

        dialog.show_all()

    def on_dialog_response(self, dialog, restoration_path, file_type_checkboxes):
        selected_file_types = [checkbox.get_label() for checkbox in file_type_checkboxes if checkbox.get_active()]
        
        # Validate the file types
        if not selected_file_types:
            self.show_error_message("You must select at least one file type.")
            return

        # Process the input values
        print(f"Restoration Path: {restoration_path}")
        print(f"Selected File Types: {', '.join(selected_file_types)}")

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

    def dry_run(self, command):
        # Create a new top-level window for the dry run
        confirm_dialog = Gtk.MessageDialog(
            parent=None,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            message_format="                     SaveMyNode\n\nA dry run simulates the recovery process without making actual changes to the filesystem.\n\n"
                           "Do you want to proceed?"
        )
        confirm_dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)

        # Wait for user response
        response = confirm_dialog.run()
        confirm_dialog.destroy()

        # If the user cancels, return early without executing the command
        if response == Gtk.ResponseType.CANCEL:
            return

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
        os.chdir("../..") # quite redundant but words



    def on_exit_clicked(self, button):
        Gtk.main_quit()

if __name__ == "__main__":
    win = SaveMyNodeApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
