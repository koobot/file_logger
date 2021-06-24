import os
import hashlib
from datetime import datetime
import sys

# Check arguments to see if hashes for files should be calculated
# Setting this as True can make program significantly slower if large files
INCLUDE_HASH = False
if len(sys.argv) > 1:
    INCLUDE_HASH = bool(sys.argv[1])

INCLUDE_SIZE = True
if len(sys.argv) > 2:
    INCLUDE_SIZE = bool(sys.argv[2])

# If not CSV then will return as txt, in a list format
CSV_FORMAT = True
if len(sys.argv) > 3:
    CSV_FORMAT = bool(sys.argv[3])

def get_hash(filename):
    '''
    Gets the hash of each file. Good for when tracking changes.
    Might significantly increase processing time!
    '''
    h = hashlib.sha1()

    with open(filename, "rb") as f:
        chunk = 0
        while chunk != b'':
            chunk = f.read(1024)
            h.update(chunk)
    return h.hexdigest()

# Store file paths by extension
files = {}

# Set of extensions
exts = set()

print("Collecting files...")

# Walk current working directory and get all file paths
# Add file paths to dictionary where key is the extension
for dirpath, _, filenames in os.walk(os.getcwd()):
    for file in filenames:
        file = file.lower()

        # Don't add this script or other audit files to the file log
        if ("file_logger.py" in file) or ("file_audit" in file) or (".git" in dirpath):
            continue

        filepath = os.path.join(dirpath, file)

        _, ext = os.path.splitext(filepath)

        exts.add(ext)

        if ext in files:
            files[ext].append(filepath)
        else:
            files[ext] = [filepath, ]

# Sort extensions
exts = sorted(list(exts))

print("Writing file paths...")

# Create unique file name and write out the data to it
fname_prefix = "file_audit_" + datetime.now().strftime("%d%m%Y_%H%M%S")

if CSV_FORMAT:
    fname = fname_prefix + ".csv"
else:
    fname = fname_prefix + ".txt"

# Set separator type depending on format
if CSV_FORMAT:
    SEP = ","
else:
    SEP = "\n"

with open(os.path.join(os.getcwd(), fname), "w+") as f:
    if CSV_FORMAT:
        f.write("file" + SEP + "ext")
        if INCLUDE_HASH:
            f.write(SEP + "hash")
        if INCLUDE_SIZE:
            f.write(SEP + "size_MB")
        f.write("\n")

    for ext in exts:
        if not CSV_FORMAT:
            f.write("-------------------\n")
            if not ext:
                f.write("Files with no extension:\n")
            else:
                f.write(ext + " files:\n")

        for file in files[ext]:
            f.write(file + SEP)

            if CSV_FORMAT:
                f.write(ext)

            if INCLUDE_HASH:
                hash_str = str(get_hash(file))
                if CSV_FORMAT:
                    f.write(SEP + hash_str)
                else:
                    f.write(SEP + "File hash: " + hash_str)

            if INCLUDE_SIZE:
                size_str = str(round(os.path.getsize(file)/float((1024*1024)), 4))
                if CSV_FORMAT:
                    f.write(SEP + size_str)
                else:
                    f.write(SEP + "File size: " + size_str + " MB")

            if CSV_FORMAT:
                f.write("\n")
            else:
                f.write("-------------------\n")

print("Done!")
print("Current locations of all files have been logged to", fname)
