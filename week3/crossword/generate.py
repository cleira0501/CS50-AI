import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for slot in self.domains:# for all the word to be solved
            for candidate in self.domains[slot].copy():# for all the possible candidates to fill the slot
                if len(candidate) != slot.length:#slot is a var with attributes found in crossword.py
                    self.domains[slot].remove(candidate)#if the length doont match up

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlaps = self.crossword.overlaps[(x,y)] #get overlaps

        if overlaps is None:# if there is no overlapping
            return revised
        else:
        # if  there is overlap cell between 2 slots
            i, j =  overlaps # get the index for overlaps
            for candidate_x in self.domains[x].copy():# for each possible word to solve x
                char_x  = candidate_x[i]# the letter of the overlap
                matched = False
                for candidate_y in self.domains[y]: # loop through all possible word to solve y
                    if candidate_y[j] == char_x: #if the char ever matches
                        matched = True
                        break
                if not matched:# is no matches
                    self.domains[x].remove(candidate_x)# remove the candidate  
                    revised = True
        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
           queue = []
           for slot in self.domains:
               for neighbor in self.crossword.neighbors(slot):
                    queue.append((slot,neighbor))
        else: 
            queue = list(arcs)
        while queue:
            (x,y) = queue.pop() #dequeue an arc to solve 
            if self.revise(x,y):# if revision is made
                if not self.domains[x]:# if domain is empty in any of the word slot in arc
                    return False
                for neighbor_slot in self.crossword.neighbors(x): #loop through all neighbors
                    if neighbor_slot != y:
                        queue.append((neighbor_slot,x))
        
        return True
            

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for word in assignment.values():# for all slots in crossword
            if not word: 
                return False
        for var in self.crossword.variables:
            if var not in assignment:
                return False
        return True
    
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = set()
        for slot, word in assignment.items():
            if len(word) != slot.length:
                return False
            if word in used_words:
                return False
            else:
                used_words.add(word)#add word into seen 
            for neighbor in self.crossword.neighbors(slot):# loop through the neighbors
                overlap = self.crossword.overlaps[(slot, neighbor)]
                if overlap is None or neighbor not in assignment:
                    continue
                else:
                    i, j = overlap
                    if word[i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        elimination_counts = {}

        for word in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue

                overlap = self.crossword.overlaps[(var, neighbor)]
                if overlap is None:
                    continue
                i, j = overlap
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        count += 1

            elimination_counts[word] = count
        return sorted(self.domains[var], key=lambda w: elimination_counts[w])

            
                

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        min_domain_num = len(self.crossword.variables)# set the min number to num of candidate words
        min_domain = []

        for var in self.domains:
            if var in assignment:# if the word slot has been assigned
                continue
            #if it hasnt been assigned yet
            if len(self.domains[var]) < min_domain_num:
                min_domain_num =  len(self.domains[var])#update min num
                min_domain = [var]
            elif len(self.domains[var]) == min_domain_num:
                min_domain.append(var)
        if len(min_domain) == 1:
            return min_domain[0]
        deg = 0
        highest_deg = []
        for slot in min_domain:
            degree = len(self.crossword.neighbors(slot))
            if degree > deg:# if it has a higer degree
                highest_deg = [slot]
                deg = degree#update deg
            elif degree == deg:
                highest_deg.append(slot)
        return highest_deg[0]



            

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.crossword.variables):
            return assignment # the end condition to end the recursion
        var = self.select_unassigned_variable(assignment)#select an unassigned var
        ordered_ls = self.order_domain_values(var, assignment)
        for value in ordered_ls:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):# if the assignment is valid
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
