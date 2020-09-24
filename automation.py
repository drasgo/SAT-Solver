import subprocess
import json
import os
import glob
from os import listdir
from os.path import isfile, join

data = {}
TIMEOUT = 300
if __name__ == "__main__":
    paths = ["temp"]
    counter = 0
    with open("experiments.json", "r") as fp:
        data = json.load(fp)
    # paths = ["temp", "tests", "tests/different_literals"]
    for temp_path in paths:
        path = os.path.abspath(temp_path)
        files = [f for f in listdir(path) if isfile(join(path, f))]
        # print(files)
        # input()
        # for file in range(31):
        for file in files:
            counter += 1
            filepath = (path + "/" + file)
            print("\n\nFile " + filepath + ". Remaining: " + str(len(files) - counter))
            if file not in data:
                data[file] = []
            for num in range(1, 33):
                print("Technique n°: " + str(num))
                recursion = ""
                backtracking = ""
                time = ""
                threads = ""
                known = ""
                flag = False

                try:
                    temp = subprocess.run(["./SAT.sh -S" + str(num) + " " + filepath],
                                          shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT)
                    # print(temp.stderr.decode())
                    # print(temp.stdout.decode())
                    output = temp.stdout.decode()
                    output_list = output.split("\n")

                    for line in output_list:
                        if "Number of recursions" in line:
                            recursion = line.split(":")[1].strip()
                        elif "Number of backtracking" in line:
                            backtracking = line.split(":")[1].strip()
                        elif "Time passed" in line:
                            time = line.split(":")[1].replace("seconds", "").strip()
                        elif "Threads used" in line:
                            threads = line.split(":")[1].strip()
                        elif "Number of known literals" in line:
                            known = line.split(":")[1].strip()
                        elif "Satisfiable" in line:
                            print("Satisfiable\n")
                            flag = True

                except subprocess.TimeoutExpired:
                    print("TIMEOUT\n")
                    time = "timeout"
                if flag is False:
                    continue
                data[file].append({
                    'technique': f'S{num}',
                    'implementation': 'linear',
                    'time': time,
                    'recursion': recursion,
                    'backtracks': backtracking,
                    'known litersls': known,
                    'satisfability': flag
                })

                with open('experiments.json', 'w') as outfile:
                    json.dump(data, outfile)
