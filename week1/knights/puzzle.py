from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
statement0 = And(AKnave, AKnight)

knowledge0 = And(
    # knowledge base
    Or(AKnave, AKnight), # A can be a knight or a knave
    Not(And(AKnave, AKnight)),# A cannot be both a knight and a knave

    #resolution: if knight then true else knave
    Biconditional(statement0, AKnight)
)


# Puzzle 1
# A says "We are both knaves."
# B says nothing.
statement1A = And(AKnave, BKnave)

knowledge1 = And(
    # A and B can be knight or knave
    Or(AKnave, AKnight), # A can be a knight or a knave
    Or(BKnave, BKnight), # B can be a knight or a knave
    Not(And(AKnave, AKnight)),# A cannot be both a knight and a knave
    Not(And(BKnave, BKnight)),# B cannot be both a knight and a knave

    #if A is saying the truth, A is knight
    Biconditional(AKnight, statement1A)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
statement2A = Or(And(AKnight, BKnight), And(AKnave, BKnave))
statement2B = Or(And(AKnave, BKnight), And(AKnight, BKnave))
knowledge2 = And(
    Or(AKnave, AKnight), # A can be a knight or a knave
    Or(BKnave, BKnight), # B can be a knight or a knave
    Not(And(AKnave, AKnight)),# A cannot be both a knight and a knave
    Not(And(BKnave, BKnight)),# B cannot be both a knight and a knave

    Biconditional(AKnight, statement2A),
    Biconditional(BKnight, statement2B)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
statement3A = Or(AKnight, AKnave)
statement3B = And(
    Biconditional(AKnight, AKnave),# A said A is a knave
    CKnave
)
statement3C = AKnight
knowledge3 = And(
    Or(AKnave, AKnight), # A can be a knight or a knave
    Or(BKnave, BKnight), # B can be a knight or a knave
    Not(And(AKnave, AKnight)),# A cannot be both a knight and a knave
    Not(And(BKnave, BKnight)),# B cannot be both a knight and a knave

    Biconditional(AKnight, statement3A),
    Biconditional(BKnight, statement3B),
    Biconditional(CKnight, statement3C),
    
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
