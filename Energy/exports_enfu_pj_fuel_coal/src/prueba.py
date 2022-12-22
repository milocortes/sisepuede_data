import os 

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)

relative_path = os.path.normpath(dir_path + " " + "../../..")
print(relative_path)

relative_path_file = os.path.join(relative_path, "wbal.csv")
print(relative_path_file)
