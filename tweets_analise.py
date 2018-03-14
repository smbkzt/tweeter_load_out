filename = 'data/all_tweets.csv'
with open(filename, 'r') as f:
    lines = f.readlines()

for number, line in enumerate(lines):
    print("\nLine number: ", number)
    splitted_line = line.split(" < - > ")
    for l in splitted_line:
        print(l)
    answer = input("Agreed or disagreed? (a/d): ")
    if answer == "a":
        with open('data/agreed.txt', 'a') as agree_file:
            agree_file.write(line)
    elif answer == "save":
        with open(filename, 'r') as f:
            lines = f.readlines()
        with open(filename, 'w') as f:
            for line in lines[number:]:
                f.write(line)
        break
    elif answer == "":
        continue
    else:
        with open('data/disagreed.txt', 'a') as disagree_file:
            disagree_file.write(line)
