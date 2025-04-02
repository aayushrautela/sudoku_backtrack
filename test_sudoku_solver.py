import unittest
from lab2_v4 import CSP, create_sudoku_csp

class TestSudokuSolver(unittest.TestCase):
    def test_easy_puzzle(self):
        """Test a simple solvable puzzle to verify basic functionality"""
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
        csp = create_sudoku_csp(puzzle)
        solution, _ = csp.solve()
        self.assertIsNotNone(solution, "Easy puzzle should have a solution")

    def test_hard_puzzle(self):
        """Test a harder puzzle to verify algorithm robustness"""
        puzzle = [
            [0, 0, 0, 0, 0, 0, 6, 8, 0],
            [0, 0, 0, 0, 7, 3, 0, 0, 9],
            [3, 0, 9, 0, 0, 0, 0, 4, 5],
            [4, 9, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 3, 0, 5, 0, 9, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 3, 6],
            [9, 6, 0, 0, 0, 0, 3, 0, 8],
            [7, 0, 0, 6, 8, 0, 0, 0, 0],
            [0, 2, 8, 0, 0, 0, 0, 0, 0]
        ]
        csp = create_sudoku_csp(puzzle)
        solution, _ = csp.solve()
        self.assertIsNotNone(solution, "Hard puzzle should have a solution")

    def test_empty_board(self):
        """Test an empty board (all zeros) - should find a valid Sudoku solution"""
        puzzle = [[0]*9 for _ in range(9)]
        csp = create_sudoku_csp(puzzle)
        solution, _ = csp.solve()
        self.assertIsNotNone(solution, "Empty board should have a solution")

    def test_almost_complete_board(self):
        """Test a board with only one missing number"""
        puzzle = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 0, 7, 9]  # Only one missing number at (8,6)
        ]
        csp = create_sudoku_csp(puzzle)
        solution, _ = csp.solve()
        self.assertIsNotNone(solution, "Almost complete board should have a solution")
        self.assertEqual(solution[(8,6)], 1, "Should correctly fill the last missing number")

    def test_unsolvable_puzzle(self):
        """Test an unsolvable puzzle (duplicate numbers in a row)"""
        puzzle = [
            [5, 5, 0, 0, 7, 0, 0, 0, 0],  # Duplicate 5s in first row
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ]
        csp = create_sudoku_csp(puzzle)
        self.assertIsNone(csp, "Invalid puzzle should return None during creation")

    def test_forward_checking(self):
        """Verify forward checking correctly reduces domains"""
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
        csp = create_sudoku_csp(puzzle)
        
        # Test domain reduction after assigning a value
        var = (0, 2)  # Cell at row 0, column 2
        value = 4
        updates = csp.forward_checking(var, value, {var: value})
        self.assertIsNotNone(updates, "Forward checking should return domain updates")
        self.assertIn((0, 5), updates, "Should affect cells in the same row")
        self.assertIn((1, 2), updates, "Should affect cells in the same 3x3 box")

    def test_visualization_steps(self):
        """Verify visualization captures all steps"""
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
        csp = create_sudoku_csp(puzzle)
        _, viz = csp.solve()
        self.assertGreater(len(viz), 0, "Should record visualization steps")
        for step in viz:
            self.assertIn('var', step, "Step should record variable assignment")
            self.assertIn('value', step, "Step should record assigned value")
            self.assertIn('board', step, "Step should record puzzle state")
            self.assertIn('updates', step, "Step should record domain updates")

if __name__ == '__main__':
    unittest.main()