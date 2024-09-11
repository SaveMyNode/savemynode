# recovery_window.py
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def open_recovery_window():
    """
    Create and show a new window with a Gtk.TextView for recovery.
    """
    recovery_window = Gtk.Window(title="Recovery")
    recovery_window.set_border_width(10)
    recovery_window.set_default_size(400, 300)

    # Create a TextView widget
    text_view = Gtk.TextView()
    text_view.set_wrap_mode(Gtk.WrapMode.WORD)

    # Add TextView to a Scrollable window
    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_size_request(400, 300)
    scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scrolled_window.add(text_view)

    # Add the ScrolledWindow to the recovery window
    recovery_window.add(scrolled_window)

    recovery_window.show_all()
