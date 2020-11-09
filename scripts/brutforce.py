import itertools
import os

def create_answers(combinaison):
    base_answers = "Public speaking is very easy.\n1 2 6 24 120 720\n1 b 214\n9\nopekma\n" + combinaison
    os.system("echo \'" + base_answers + "\' > answers")

def try_answer():
    os.system("./bomb answers > bomb_result")
    os.system("grep \'Congratulations!\' bomb_result > grep_result")

def has_defeated_the_bomb():
    with open("grep_result") as file_descriptor:
        grep_result = file_descriptor.read()
        if len(grep_result) > 1:
            return True
        else:
            return False

numbers = [1, 2, 3, 4, 5, 6]
permutations = list(itertools.permutations(numbers))

for permutation in permutations:
    if permutation[0] != 4:
        continue

    string_permutation = [str(number) for number in permutation]
    space = " "
    combinaison = space.join(string_permutation)
    create_answers(combinaison)
    try_answer()

    if has_defeated_the_bomb():
        print(combinaison)
        exit(0)
