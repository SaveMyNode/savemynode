import gi
import subprocess
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class SaveMyNodeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="SaveMyNode - File Recovery Tool")
        self.set_border_width(10)
        self.set_default_size(800, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        self.create_selection_section(main_box)
        self.create_details_section(main_box)
        self.create_recovery_section(main_box)
        self.create_controls_section(main_box)

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
            print(f"Error populating drives: {e}")

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
                buffer = self.details_textview.get_buffer()
                buffer.set_text("Error: Unable to retrieve partition details")
        except Exception as e:
            buffer = self.details_textview.get_buffer()
            buffer.set_text(f"Error: {e}")

    def create_recovery_section(self, parent_box):
        frame = Gtk.Frame(label="File Recovery")
        parent_box.pack_start(frame, False, False, 10)

        recovery_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame.add(recovery_box)

        # Recovery Path
        recovery_path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        recovery_box.pack_start(recovery_path_box, False, False, 0)

        recovery_path_label = Gtk.Label(label="Recovery Path:")
        recovery_path_box.pack_start(recovery_path_label, False, False, 0)

        self.recovery_path_entry = Gtk.Entry()
        recovery_path_box.pack_start(self.recovery_path_entry, True, True, 0)

        recovery_path_button = Gtk.Button(label="Choose")
        recovery_path_button.connect("clicked", self.on_recovery_path_button_clicked)
        recovery_path_box.pack_start(recovery_path_button, False, False, 0)

        # Target Directory
        target_directory_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        recovery_box.pack_start(target_directory_box, False, False, 0)

        target_directory_label = Gtk.Label(label="Target Directory:")
        target_directory_box.pack_start(target_directory_label, False, False, 0)

        self.target_directory_entry = Gtk.Entry()
        target_directory_box.pack_start(self.target_directory_entry, True, True, 0)

        target_directory_button = Gtk.Button(label="Choose")
        target_directory_button.connect("clicked", self.on_target_directory_button_clicked)
        target_directory_box.pack_start(target_directory_button, False, False, 0)

        self.recovery_log_textview = Gtk.TextView()
        self.recovery_log_textview.set_editable(False)
        self.recovery_log_textview.set_cursor_visible(False)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_size_request(550, 150)
        scrolled_window.add(self.recovery_log_textview)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        recovery_box.pack_start(scrolled_window, False, False, 10)

    def create_controls_section(self, parent_box):
        button_box = Gtk.Box(spacing=10)
        parent_box.pack_start(button_box, False, False, 10)

        self.start_button = Gtk.Button(label="Start Recovery")
        self.start_button.connect("clicked", self.on_start_recovery_clicked)
        button_box.pack_start(self.start_button, False, False, 0)

        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", self.on_exit_clicked)
        button_box.pack_start(exit_button, False, False, 0)

    def on_recovery_path_button_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Recovery Path",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.recovery_path_entry.set_text(dialog.get_filename())
        dialog.destroy()

    def on_target_directory_button_clicked(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select Target Directory",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.target_directory_entry.set_text(dialog.get_filename())
        dialog.destroy()

    def on_start_recovery_clicked(self, button):
        self.drive_path = self.drive_combo.get_active_text().split()[0]
        self.filesystem_type = self.filesystem_combo.get_active_text()
        recovery_path = self.recovery_path_entry.get_text()
        target_directory = self.target_directory_entry.get_text()

        if self.filesystem_type and self.drive_path and recovery_path and target_directory:
            append_log(self.recovery_log_textview, f"Starting recovery from {recovery_path} to {target_directory} on {self.drive_path} ({self.filesystem_type})...")
            if self.filesystem_type == "Btrfs":
                recover_btrfs(self.drive_path, self.recovery_log_textview, recovery_path, target_directory)
            elif self.filesystem_type == "XFS":
                recover_xfs(self.drive_path, self.recovery_log_textview, recovery_path, target_directory)
        else:
            append_log(self.recovery_log_textview, "Error: Select a valid filesystem, drive, and specify both the recovery path and target directory.")

    def on_exit_clicked(self, button):
        Gtk.main_quit()

def append_log(textview, message):
    buffer = textview.get_buffer()
    buffer.insert(buffer.get_end_iter(), message + "\n")

def recover_btrfs(drive_path, log_textview, recovery_path, target_directory):
    append_log(log_textview, f"Simulating Btrfs recovery from {recovery_path} to {target_directory} on {drive_path}...")

def recover_xfs(drive_path, log_textview, recovery_path, target_directory):
    append_log(log_textview, f"Simulating XFS recovery from {recovery_path} to {target_directory} on {drive_path}...")

if __name__ == "__main__":
    app = SaveMyNodeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
