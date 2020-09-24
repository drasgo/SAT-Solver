
for file in range(21):
    with open(f"sudoku-ex-{file}.out", "r") as f:
        with open("sudoku-rules.txt", "r") as g:
            rules = g.read()
            content = f.read()
            content_list = content.split(" ")
            if 5 <= len(content_list) <= 81:
                # print(content_list)
                while content_list:
                    with open(f"tests/sudoku-ex-{file}-{len(content_list)}.txt", "w") as p:
                        p.write(rules)
                        for number in content_list:
                            p.write(f"{number} 0")
                            p.write("\n")
                    content_list.pop()
