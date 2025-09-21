import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count !=0:
            # print(f"Known mines from sentence: {self.cells}")
            return self.cells
        return set()
       

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            # print(f"known safe{self.cells}")
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            self.count -=1
            self.cells.remove(cell) 
        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        # print(f"Marking mine: {cell}")
        for sentence in self.knowledge:
            sentence.mark_mine(cell)
            
        

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        # print(f"Marking safe: {cell}")
        for sentence in self.knowledge:
            if cell in sentence.cells:
                sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)#1
        self.mark_safe(cell)#2
        #formulating a new statement to be added to knowledge base
        neighbors = set()
        #check all neighboring cells
        for i in range(cell[0]-1, cell[0]+2):
            for j in range(cell[1]-1, cell[1]+2):
                if (i,j) == cell:#ignor the cell itself
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:#check in bounds
                    if (i,j) in self.safes:
                        continue
                    if (i, j) in self.moves_made:
                        continue
                    if (i,j) in self.mines:
                        count-=1
                    else:#new info
                        neighbors.add((i,j))
    
        new_sentence = Sentence(neighbors, count)
        # print(f"Adding new sentence: {new_sentence.cells, new_sentence.count}")
        self.knowledge.append(new_sentence)



        #inference while loop 
        #first mark all safes and mines

        changed = True
        while changed:
            changed = False#reset it so the default is not to start again the loop
            for sentence in self.knowledge:# loop through all sentences
                for safe in list(sentence.known_safes()):#if there are safes, loop through safe cells
                    self.mark_safe(safe)
                    changed = True
                for mine in list(sentence.known_mines()):
                    self.mark_mine(mine)
                    changed = True
            
            # we have two sentences set1 = count1 and set2 = count2 where set1 is a subset of set2
            # then we can construct the new sentence set2 - set1 = count2 - count1
            # resolution 
            new_knowledge = []#initiate a holder
            for s1, s2 in list(itertools.permutations(self.knowledge, 2)):
                # print(f"sentences{sentence1.cells, sentence2.cells}")
                if s1 == s2:
                    continue
                if s1.cells.issubset(s2.cells):
                    # print("is subset")
                    new_sentence = Sentence((s2.cells- s1.cells), (s2.count - s1.count))
                    if (
                        new_sentence.cells 
                        and new_sentence not in self.knowledge 
                        and new_sentence != s1 
                        and new_sentence != s2
                        ):
                        new_knowledge.append(new_sentence)
                        # print(f"changing sentence: {new_sentence.cells, new_sentence.count}")
                        changed = True
            self.knowledge.extend(new_knowledge)

                

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        avail_set = self.safes.difference(self.moves_made)
        if avail_set:
            # print(f"Making safe move: {avail_set}")
            return random.choice(list(avail_set))
        else:
            return None
            
  
    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set(itertools.product(range(self.height), range(self.width)))
        avail_cells = all_cells - self.moves_made.union(self.mines)
        if avail_cells:
            return random.choice(list(avail_cells))
