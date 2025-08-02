import os
import re
import datetime

def sanitize_filename(name):
    return re.sub(r'[\/:"*?<>|]+', '_', name)

def create_output_folder(base_dir=None):
    import datetime, os
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if base_dir is None:
        base_dir = "D:\\flipkart_ss"
    path = os.path.join(base_dir, now)
    os.makedirs(path, exist_ok=True)
    return path
