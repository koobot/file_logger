import os
import hashlib
from datetime import datetime
import sys
from distutils import util

# Check arguments to see if hashes for files should be calculated
# Setting this as True can make program significantly slower if large files
INCLUDE_HASH = False
if len(sys.argv) > 1:
    INCLUDE_HASH = bool(util.strtobool(sys.argv[1]))

INCLUDE_SIZE = True
if len(sys.argv) > 2:
    INCLUDE_SIZE = bool(util.strtobool(sys.argv[2]))

# If not CSV then will return as txt, in a list format
CSV_FORMAT = True
if len(sys.argv) > 3:
    CSV_FORMAT = bool(util.strtobool(sys.argv[3]))

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

def write_csv(output, paths=files, sep=SEP, include_hash=INCLUDE_HASH, include_size=INCLUDE_SIZE):
    '''
    Write CSV format. Assumes it's being used in `with open()` statement
    '''
    # Header
    output.write("file" + sep + "ext")
    if include_hash:
        output.write(sep + "hash")
    if include_size:
        output.write(sep + "size_MB")
    output.write("\n")

    # Body
    for extension, filepaths in paths.items():
        for path in filepaths:
            output.write(path + sep + extension)

            if include_hash:
                output.write(sep + str(get_hash(path)))
            if include_size:
                output.write(sep + str(round(os.path.getsize(path)/float((1024*1024)), 4)))
            output.write("\n")

def write_txt(output, extensions=exts, paths=files, sep=SEP, include_hash=INCLUDE_HASH, include_size=INCLUDE_SIZE):
    '''
    Write text file format. Assumes it's being used in `with open()` statement
    '''
    for ext in extensions:
        output.write("-------------------" + sep)
        if not ext:
            output.write("Files with no extension:\n")
        else:
            output.write(ext + " files:\n")

        for path in paths[ext]:
            output.write(path + sep)

            if include_hash:
                output.write(sep + "File hash: " + str(get_hash(path)))
            if include_size:
                output.write(sep + "File size: " + str(round(os.path.getsize(path)/float((1024*1024)), 4)))

        output.write("-------------------" + sep + sep)
    

with open(os.path.join(os.getcwd(), fname), "w+") as f:
    if CSV_FORMAT:
        write_csv(output=f)
    else:
        write_txt(output=f)

print("Done!")
print("Current locations of all files have been logged to", fname)
