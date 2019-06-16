from filelock import FileLock

with FileLock("myfile.txt"):
    print("Lock acquired.")