import pathlib, os


for path in pathlib.Path(os.getcwd()).parents:
    if os.path.isdir(os.path.join(path, ".git")):
        print(str(path))
