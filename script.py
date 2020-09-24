with open("1000 sudokus.txt", "r") as f:
    with open("sudoku-rules.txt", "r") as g:
        rules = g.read()
        content = f.read()
        content_list = content.split("\n")
        for i in range(len(content_list)):
            row = 1
            colom = 1
            with open(f"sudok-ex-{i}.txt", "w") as p:
                p.write(rules)
                for j in content_list[i]:
                    if j != ".":
                        p.write(f"{row}{colom}{j} 0")
                        p.write("\n")
                    colom += 1
                    if colom > 9:
                        row += 1
                        colom = 1
        
        
            
            


            
