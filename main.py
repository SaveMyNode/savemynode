import gi
import subprocess
from recovery_operations import recover_btrfs, recover_xfs
from log_helper import append_log

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

class SaveMyNodeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SaveMyNode")
        self.set_border_width(15)
        self.set_default_size(600, 500)
        
        # Apply CSS theme
        self.apply_theme()

        # Stack for screen transitions
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        # Initial Welcome screen
        intro_screen = self.create_intro_screen()
        self.stack.add_named(intro_screen, "intro")


        # Main UI screen
        main_screen = self.create_main_screen()
        self.stack.add_named(main_screen, "main")
       
         
        self.add(self.stack)

        self.drive_path = None
        self.filesystem_type = None

        # Show intro screen first and transition to main screen
        GLib.timeout_add(1500, self.show_main_screen)
        


    def apply_theme(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("styles.css")
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_intro_screen(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)

        title = Gtk.Label(label="<big><b>Welcome to SaveMyNode</b></big>")
        title.set_use_markup(True)
        box.pack_start(title, False, False, 0)

        description = Gtk.Label(label="Recover deleted files from BTRFS and XFS partitions.")
        box.pack_start(description, False, False, 10)

        spinner = Gtk.Spinner()
        spinner.start()
        box.pack_start(spinner, False, False, 0)

        return box
    def show_main_screen(self):
        self.stack.set_visible_child_name("main")
        return False 

    def create_main_screen(self):
        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # File system and drive selection
        self.create_selection_section(main_box)

        # File system details section
        self.create_details_section(main_box)

        # Recovery section
        self.create_recovery_section(main_box)

        # Adding additional controls section
        self.create_controls_section(main_box)

        # Adding the scrollable window to the main screen
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(main_box)
        scrolled_window.get_style_context().add_class("scrolled-window")

        return scrolled_window

    def create_selection_section(self, parent_box):
        frame = Gtk.Frame(label="Select Filesystem and Drive")
        parent_box.pack_start(frame, False,False, 10)

        selection_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame.add(selection_box)

        # Filesystem selection with fade-in effect
        fs_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        fs_label = Gtk.Label(label="Filesystem:")
        fs_box.pack_start(fs_label, False, False, 30)
        self.filesystem_combo = Gtk.ComboBoxText()
        self.filesystem_combo.append_text("Btrfs")
        self.filesystem_combo.append_text("XFS")
        self.filesystem_combo.set_active(0)

        fs_box.pack_start(fs_label, True, True, 45)
        fs_box.pack_start(self.filesystem_combo, True, True, 10)
        spacer = Gtk.Label()  # Acts as a dynamic spacer
        fs_box.pack_start(spacer, False, False, 100)
        selection_box.pack_start(fs_box, True, True, 10)


        # Drive selection with smooth scrolling
        drive_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        drive_label = Gtk.Label(label="Drive:")
        drive_box.pack_start(drive_label, False, False, 30)
        self.drive_combo = Gtk.ComboBoxText()
        self.populate_drive_combo()
        self.drive_combo.set_size_request(350, -1)
        drive_box.pack_start(self.drive_combo, True, True, 45)
        selection_box.pack_start(drive_box, False, False, 10)
        spacer = Gtk.Label()  # Acts as a dynamic spacer
        drive_box.pack_start(spacer, False, False, 80)

    def create_details_section(self, parent_box):
        frame = Gtk.Frame(label="Partition Details")
        parent_box.pack_start(frame, True, True, 10)

        self.details_textview = Gtk.TextView()
        self.details_textview.set_editable(False)
        self.details_textview.set_cursor_visible(False)

        # Scrolling with kinetic effect
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(550, 150)
        scrolled_window.add(self.details_textview)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        frame.add(scrolled_window)


        # Add partition details initially
        GLib.timeout_add(500, self.update_partition_details)  # Delayed for dynamic update

    def create_recovery_section(self, parent_box):
        frame = Gtk.Frame(label="File Recovery")
        parent_box.pack_start(frame, False, False, 10)

        recovery_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame.add(recovery_box)

        # Start recovery button with pulse animation
        self.recovery_button = Gtk.Button(label="Start Recovery")
        self.recovery_button.connect("clicked", self.on_recover_clicked)
        self.recovery_button.set_size_request(150, -1)
        recovery_box.pack_start(self.recovery_button, False, False, 10)

        # Output text view with smooth scrolling
        self.output_textview = Gtk.TextView()
        self.output_textview.set_editable(False)
        self.output_textview.set_cursor_visible(False)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(550, 150)
        scrolled_window.add(self.output_textview)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        recovery_box.pack_start(scrolled_window, True, True, 10)

    def create_controls_section(self, parent_box):
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        parent_box.pack_start(controls_box, False, False, 10)

        # Clear Log Button
        clear_log_button = Gtk.Button(label="Clear Log")
        clear_log_button.connect("clicked", self.on_clear_log_clicked)
        controls_box.pack_start(clear_log_button, False, False, 10)

        # Refresh Partition Details Button
        refresh_button = Gtk.Button(label="Refresh Partition Details")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        controls_box.pack_start(refresh_button, False, False, 10)

    def populate_drive_combo(self):
        try:
            output = subprocess.check_output(["lsblk", "-nlo", "NAME,SIZE,TYPE"], universal_newlines=True)
            lines = output.strip().split("\n")
            for line in lines:
                parts = line.split()
                if len(parts) == 3 and parts[2] in ["part"]:
                    name, size, _ = parts
                    self.drive_combo.append_text(f"/dev/{name} ({size})")
        except subprocess.CalledProcessError:
            print("Error: Unable to retrieve drive information")

    def update_partition_details(self):
        try:
            output = subprocess.check_output(["lsblk", "-o", "NAME,FSTYPE,LABEL,SIZE,TYPE,MOUNTPOINT"], universal_newlines=True)
            buffer = self.details_textview.get_buffer()
            buffer.set_text(output)
        except subprocess.CalledProcessError:
            buffer = self.details_textview.get_buffer()
            buffer.set_text("Error: Unable to retrieve partition details.")

    def on_recover_clicked(self, widget):
        selected_drive = self.drive_combo.get_active_text()
        if not selected_drive:
            append_log(self.output_textview.get_buffer(), "Error: No drive selected.")
            return
        
        self.drive_path = selected_drive.split()[0]
        self.filesystem_type = self.filesystem_combo.get_active_text()
        
        append_log(self.output_textview.get_buffer(), f"Starting recovery on {self.drive_path} ({self.filesystem_type})...")

        # Simulate recovery progress
        self.recovery_button.set_label("Recovering...")
        GLib.timeout_add(3000, self.finish_recovery)

    def finish_recovery(self):
        if self.filesystem_type == "Btrfs":
            result = recover_btrfs(self.drive_path)
        elif self.filesystem_type == "XFS":
            result = recover_xfs(self.drive_path)
            
            

        append_log(self.output_textview.get_buffer(), result)
        self.recovery_button.set_label("Start Recovery")
        return False  # Stop the timeout

    def on_clear_log_clicked(self, widget):
        # Clear the log text view
        self.output_textview.get_buffer().set_text("")

    def on_refresh_clicked(self, widget):
        # Refresh the partition details
        self.update_partition_details()
        self.output_textview.get_buffer().set_text("Partition table view refreshed.")

if __name__ == "__main__":
    win = SaveMyNodeApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
