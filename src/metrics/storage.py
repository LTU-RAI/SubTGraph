import os

root = "lavatube"
csv = open(os.path.join(".", root + ".csv"), "w")
csv.write("folder\tbytes\n")
for folder in os.listdir(os.path.join(".", root)):
    file = open(os.path.join(root, folder, "subtgraph.obj"), 'r')
    size = file.readlines()[2].split(" ")[1]

    csv.write(f"{folder}\t{size}")
    file.close()
csv.close()