import gi
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

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

        selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        frame.add(selection_box)

        filesystem_label = Gtk.Label(label="Filesystem:")
        selection_box.pack_start(filesystem_label, False, False, 0)

        self.filesystem_combo = Gtk.ComboBoxText()
        self.filesystem_combo.append_text("Btrfs")
        self.filesystem_combo.append_text("XFS")
        selection_box.pack_start(self.filesystem_combo, False, False, 0)

        drive_label = Gtk.Label(label="Drive:")
        selection_box.pack_start(drive_label, False, False, 0)

        self.drive_combo = Gtk.ComboBoxText()
        self.populate_drive_combo()
        selection_box.pack_start(self.drive_combo, False, False, 0)

    def populate_drive_combo(self):
        try:
            result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,SIZE,MOUNTPOINT"], capture_output=True, text=True)
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

    def refresh_partition_details(self):
        try:
            result = subprocess.run(["lsblk", "-o", "NAME,FSTYPE,LABEL,SIZE,TYPE,MOUNTPOINT"], capture_output=True, text=True)
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

        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", self.on_exit_clicked)
        button_box.pack_start(exit_button, False, False, 0)

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
            "   - Choose the filesystem type (Btrfs or XFS) from the dropdown.\n"
            "   - Select the drive from the dropdown list.\n\n"
            "2. Partition Details:\n"
            "   - This section displays the details of the partitions on the selected drive.\n\n"
            "3. File Recovery:\n"
            "   - Specify the recovery path where files will be recovered from.\n"
            "   - Specify the target directory where files will be recovered to.\n"
            "   - Click 'Choose' buttons to select directories using a file chooser dialog.\n\n"
            "4. Start Recovery:\n"
            "   - Click 'Start Recovery' to begin the recovery process.\n\n"
            "5. Exit:\n"
            "   - Click 'Exit' to close the application."
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
        # Simulate gathering statistics
        buffer = self.stats_textview.get_buffer()
        # have to implement our own function to display statistics
        buffer.set_text(f"Drive Statistics for {drive_text}:\n\n- Total Space: 500 GB\n- Used: 120 GB\n- Free: 380 GB")

    def on_inode_recovery_clicked(self, button):
        print("Inode recovery started.")

    def on_partition_recovery_clicked(self, button):
        print("Partition recovery started.")

    def on_exit_clicked(self, button):
        Gtk.main_quit()

if __name__ == "__main__":
    win = SaveMyNodeApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
