import random
while (i := input("rock, paper, scissors? (or quit) ").lower()) != "quit":
    if i not in (choices := ['rock', 'paper', 'scissors']): print("wrong choice"); continue
    print(f"computer: {(c := random.choice(choices))}, "
          f"{'tie' if i == c else 'win' if (i, c) in [('rock', 'scissors'), ('scissors', 'paper'), ('paper', 'rock')] else 'lost'}")