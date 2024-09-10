# log_helper.py

def append_log(buffer, text):
    buffer.insert(buffer.get_end_iter(), text + "\n")
