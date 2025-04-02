import copy # Import copy module for deep copying puzzle

class CSP:
    def __init__(self, variables, domains, constraints, initial_puzzle):
        """Constraint Satisfaction Problem solver for Sudoku"""
        self.variables = variables
        # Store a deep copy of the initial domains to allow resetting if needed (though not used in this version)
        self.initial_domains = copy.deepcopy(domains)
        self.domains = domains
        self.constraints = constraints
        # Store the initial puzzle state
        self.initial_puzzle = initial_puzzle
        self.solution = None
        self.viz = []

    @staticmethod
    def print_sudoku(puzzle):
        """Print formatted sudoku puzzle"""
        for i in range(9):
            if i % 3 == 0 and i != 0:
                print("- - - - - - - - - - -")
            for j in range(9):
                if j % 3 == 0 and j != 0:
                    print(" | ", end="")
                cell_value = puzzle[i][j]
                print(int(cell_value) if isinstance(cell_value, (int, float)) and cell_value != 0 else '.', end=" ")
            print()

    def visualize(self):
        """Show step-by-step solving visualization with highlighted changes"""
        if not self.viz:
            print("\nNo visualization steps recorded (perhaps the puzzle was solved immediately or is unsolvable).")
            return

        print("\nSolving steps visualization (changes marked with *):\n")
        prev_board = [row[:] for row in self.initial_puzzle]
        
        for step in self.viz:
            r, c = step['var']
            print(f"Step {step['step']}: Assign cell {step['var']} = \033[1m{step['value']}\033[0m")
            
            # Highlight the changed cell with *
            print("Board state (changed cell marked):")
            for i in range(9):
                if i % 3 == 0 and i != 0:
                    print("- - - - - - - - - - -")
                for j in range(9):
                    if j % 3 == 0 and j != 0:
                        print(" | ", end="")
                    cell_value = step['board'][i][j]
                    prefix = "*" if (i,j) == (r,c) else " "
                    print(f"{prefix}{int(cell_value) if isinstance(cell_value, (int, float)) and cell_value != 0 else '.'}", end=" ")
                print()
            
            # Show what changed from previous step
            print("\nChanges from previous step:")
            changed = False
            for i in range(9):
                for j in range(9):
                    if step['board'][i][j] != prev_board[i][j]:
                        print(f"  - Cell ({i},{j}): {prev_board[i][j] if prev_board[i][j] != 0 else '.'} → {step['board'][i][j]}")
                        changed = True
            if not changed:
                print("  - No cell value changes (only domain reductions)")
            
            # Print domain updates
            print("\nDomain updates:")
            if step['updates']:
                for cell, domain in step['updates'].items():
                    print(f"  - Cell {cell}: Domain reduced to {domain}")
            else:
                print("  - No domain updates in this step.")
            
            print("-" * 40) # Separator
            prev_board = [row[:] for row in step['board']]


    def solve(self):
        """Solve puzzle and return solution with visualization steps"""
        # Start with an empty assignment
        assignment = {}
        # Call the backtracking algorithm
        self.solution = self.backtrack(assignment)
        # Return the solution dictionary and visualization steps
        return self.solution, self.viz

    def forward_checking(self, var, value, assignment):
        """Perform forward checking by reducing neighbor domains"""
        updates = {}
        # Iterate through all neighbors constrained by 'var'
        # self.constraints[var] contains all cells in the same row, col, and box
        for neighbor in self.constraints[var]:
            # Check if the neighbor is unassigned and is an actual variable
            if neighbor not in assignment and neighbor in self.domains:
                # Check if the assigned 'value' is currently in the neighbor's domain
                if value in self.domains[neighbor]:
                    # Create the new domain by removing 'value'
                    new_domain = [v for v in self.domains[neighbor] if v != value]

                    # Check for inconsistency (empty domain)
                    if not new_domain:
                        # If removing 'value' results in an empty domain, this path is invalid
                        return None # Signal failure

                    # Record the domain update for this neighbor
                    updates[neighbor] = new_domain

        # Return the dictionary of domain updates
        return updates


    def backtrack(self, assignment):
        """Backtracking with MRV heuristic and forward checking"""
        # Base case: If assignment is complete (all variables assigned)
        if len(assignment) == len(self.variables):
            return assignment # Solution found

        # Variable Selection: Select unassigned variable using MRV heuristic
        unassigned = [v for v in self.variables if v not in assignment]
        # Find the variable with the Minimum Remaining Values (smallest domain)
        var = min(unassigned, key=lambda v: len(self.domains[v]))

        # Value Ordering: Order domain values using LCV heuristic
        # Sort values by the number of choices they eliminate for neighbors (least constraining first)
        domain_ordered = sorted(self.domains[var],
                                key=lambda val: sum(1 for neighbor in self.constraints[var]
                                                    if neighbor not in assignment and neighbor in self.domains and val in self.domains[neighbor]))

        # Try assigning each value in the ordered domain
        for value in domain_ordered:
            # --- Visualization: Capture state BEFORE making the assignment ---
            # Create the board state reflecting the potential assignment
            current_board = [row[:] for row in self.initial_puzzle] # Start with initial puzzle
            for (r, c), val_assigned in assignment.items(): # Add current assignments
                current_board[r][c] = val_assigned
            current_board[var[0]][var[1]] = value # Add the potential assignment

            # --- Consistency Check: Perform Forward Checking ---
            # Temporarily add the assignment to check its consequences
            assignment[var] = value
            updates = self.forward_checking(var, value, assignment)
            # Remove the temporary assignment (it will be added back if check passes)
            del assignment[var]

            # Check if forward checking found an inconsistency (updates is None)
            if updates is not None:
                # --- Consistent: Apply updates and recurse ---

                # 1. Save the current domains of cells that will be updated
                #    Needed for backtracking if the recursive call fails.
                saved_domains = {cell: self.domains[cell][:] for cell in updates} # Use slicing for list copy

                # 2. Apply the domain updates found by forward checking
                for cell, new_domain in updates.items():
                    self.domains[cell] = new_domain

                # 3. Record visualization step AFTER successful forward check
                self.viz.append({
                    'step': len(self.viz) + 1,
                    'var': var,
                    'value': value,
                    'board': current_board, # Use the board state captured earlier
                    'updates': updates # Record which domains were pruned
                })

                # 4. Make the assignment permanent for this path
                assignment[var] = value

                # 5. Recursive call for the next variable
                result = self.backtrack(assignment)

                # 6. Check if recursion found a solution
                if result is not None:
                    return result # Pass the solution back up

                # --- Backtrack: If recursive call failed ---
                # a. Remove the current assignment
                del assignment[var]
                # b. Restore the domains that were modified by forward checking
                for cell, original_domain in saved_domains.items():
                    self.domains[cell] = original_domain

            # If forward checking failed (updates is None), continue to the next value in the domain

        # If no value for 'var' leads to a solution, return None (failure)
        return None


def create_sudoku_csp(puzzle):
    """Create CSP instance from Sudoku puzzle"""
    is_valid = True
    rows, cols, boxes = [set() for _ in range(9)], [set() for _ in range(9)], [set() for _ in range(9)]

    for r in range(9):
        for c in range(9):
            val = puzzle[r][c]
            if val != 0:
                if val in rows[r]: is_valid = False; break
                rows[r].add(val)
                if val in cols[c]: is_valid = False; break
                cols[c].add(val)
                box_index = (r // 3) * 3 + (c // 3)
                if val in boxes[box_index]: is_valid = False; break
                boxes[box_index].add(val)
        if not is_valid: break

    if not is_valid:
        print("Error: Initial puzzle configuration is invalid (duplicates found).")
        return None

    variables = [(r, c) for r in range(9) for c in range(9) if puzzle[r][c] == 0]
    domains = {var: list(range(1, 10)) for var in variables}
    constraints = {}
    
    for var in variables:
        r, c = var
        constrained_cells = set()
        
        # Add row and column constraints
        for i in range(9):
            if i != c: constrained_cells.add((r, i))
            if i != r: constrained_cells.add((i, c))
            
        # Add box constraints
        start_row, start_col = 3 * (r // 3), 3 * (c // 3)
        for row_idx in range(start_row, start_row + 3):
            for col_idx in range(start_col, start_col + 3):
                if (row_idx, col_idx) != var:
                    constrained_cells.add((row_idx, col_idx))
                    
        constraints[var] = constrained_cells

    # Apply initial constraints from pre-filled cells
    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0:
                val = puzzle[r][c]
                neighbors = set()
                
                # Add all cells in same row, column and box
                for i in range(9):
                    neighbors.add((r, i))
                    neighbors.add((i, c))
                
                start_row, start_col = 3 * (r // 3), 3 * (c // 3)
                for row_idx in range(start_row, start_row + 3):
                    for col_idx in range(start_col, start_col + 3):
                        neighbors.add((row_idx, col_idx))
                
                # Remove value from neighbors' domains
                for neighbor in neighbors:
                    if neighbor in domains and val in domains[neighbor]:
                        domains[neighbor].remove(val)

    return CSP(variables, domains, constraints, puzzle)

if __name__ == "__main__":
    # Example puzzle
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]

    # Harder puzzle example
    # puzzle = [
    #     [0, 0, 0, 0, 0, 0, 6, 8, 0],
    #     [0, 0, 0, 0, 7, 3, 0, 0, 9],
    #     [3, 0, 9, 0, 0, 0, 0, 4, 5],
    #     [4, 9, 0, 0, 0, 0, 0, 0, 0],
    #     [8, 0, 3, 0, 5, 0, 9, 0, 2],
    #     [0, 0, 0, 0, 0, 0, 0, 3, 6],
    #     [9, 6, 0, 0, 0, 0, 3, 0, 8],
    #     [7, 0, 0, 6, 8, 0, 0, 0, 0],
    #     [0, 2, 8, 0, 0, 0, 0, 0, 0]
    # ]

    # Invalid puzzle example (duplicate 5 in first row)
    # puzzle = [
    #     [5, 5, 0, 0, 7, 0, 0, 0, 0],
    #     [6, 0, 0, 1, 9, 5, 0, 0, 0],
    #     [0, 9, 8, 0, 0, 0, 0, 6, 0],
    #     [8, 0, 0, 0, 6, 0, 0, 0, 3],
    #     [4, 0, 0, 8, 0, 3, 0, 0, 1],
    #     [7, 0, 0, 0, 2, 0, 0, 0, 6],
    #     [0, 6, 0, 0, 0, 0, 2, 8, 0],
    #     [0, 0, 0, 4, 1, 9, 0, 0, 5],
    #     [0, 0, 0, 0, 8, 0, 0, 7, 9]
    # ]

    print('Initial puzzle:')
    CSP.print_sudoku(puzzle) # Use the static method

    print('\nAttempting to solve...')
    # Create the CSP instance. create_sudoku_csp now returns None for invalid puzzles.
    csp = create_sudoku_csp(puzzle)

    # *** FIX 1: Check if CSP creation was successful ***
    if csp is None:
        # No need to print message here, create_sudoku_csp already did
        pass # Exit or handle error appropriately
    else:
        # Solve the puzzle
        sol, viz = csp.solve() # sol is the dictionary {(r, c): value} or None

        print('\n******* Solution *******')
        # *** FIX 2: Check if the solver returned a solution dictionary ***
        if sol is not None:
            # *** FIX 3: Reconstruct the solution board correctly ***
            # Start with a deep copy of the original puzzle
            solution_board = [row[:] for row in puzzle]
            # Fill in the solved values from the solution dictionary
            for (r, c), val in sol.items():
                solution_board[r][c] = val

            # Print the completed board
            CSP.print_sudoku(solution_board)

            # Show solving steps visualization
            print("\nShowing solving steps...")
            csp.visualize()
        else:
            # This handles both initially invalid puzzles (if create_sudoku_csp didn't return None but led to empty domains)
            # and puzzles that are genuinely unsolvable.
            print("No solution exists for this puzzle.")