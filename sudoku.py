# GUI.py
import pygame
from random import shuffle
import numpy as np
import copy
from solver import *
import time
pygame.font.init()

class SudokuGenerator:
	"""generates and solves Sudoku puzzles using a backtracking algorithm"""
	def __init__(self,grid=None):
		self.counter = 0
		#path is for the matplotlib animation
		self.path = []
		#if a grid/puzzle is passed in, make a copy and solve it
		if grid:
			if len(grid[0]) == 9 and len(grid) == 9:
				self.grid = grid
				self.original = copy.deepcopy(grid)
				self.solve_input_sudoku()
			else:
				print("input needs to be a 9x9 matrix")
		else:
			#if no puzzle is passed, generate one
			self.grid = [[0 for i in range(9)] for j in range(9)]
			self.generate_puzzle()
			self.original = copy.deepcopy(self.grid)
		
		
	def solve_input_sudoku(self):
		"""solves a puzzle"""
		self.generate_solution(self.grid)
		return
	def generate_puzzle(self):
		"""generates a new puzzle and solves it"""
		self.generate_solution(self.grid)
		self.remove_numbers_from_grid()
		return

	def print_grid(self, grid_name=None):
		if grid_name:
			print(grid_name)
		for row in self.grid:
			print(row)
		return

	def test_sudoku(self,grid):
		"""tests each square to make sure it is a valid puzzle"""
		for row in range(9):
			for col in range(9):
				num = grid[row][col]
				#remove number from grid to test if it's valid
				grid[row][col] = 0
				if not self.valid_location(grid,row,col,num):
					return False
				else:
					#put number back in grid
					grid[row][col] = num
		return True

	def num_used_in_row(self,grid,row,number):
		"""returns True if the number has been used in that row"""
		if number in grid[row]:
			return True
		return False

	def num_used_in_column(self,grid,col,number):
		"""returns True if the number has been used in that column"""
		for i in range(9):
			if grid[i][col] == number:
				return True
		return False

	def num_used_in_subgrid(self,grid,row,col,number):
		"""returns True if the number has been used in that subgrid/box"""
		sub_row = (row // 3) * 3
		sub_col = (col // 3)  * 3
		for i in range(sub_row, (sub_row + 3)): 
			for j in range(sub_col, (sub_col + 3)): 
				if grid[i][j] == number: 
					return True
		return False

	def valid_location(self,grid,row,col,number):
		"""return False if the number has been used in the row, column or subgrid"""
		if self.num_used_in_row(grid, row,number):
			return False
		elif self.num_used_in_column(grid,col,number):
			return False
		elif self.num_used_in_subgrid(grid,row,col,number):
			return False
		return True

	def find_empty_square(self,grid):
		"""return the next empty square coordinates in the grid"""
		for i in range(9):
			for j in range(9):
				if grid[i][j] == 0:
					return (i,j)
		return

	def solve_puzzle(self, grid):
		"""solve the sudoku puzzle with backtracking"""
		for i in range(0,81):
			row=i//9
			col=i%9
			#find next empty cell
			if grid[row][col]==0:
				for number in range(1,10):
					#check that the number hasn't been used in the row/col/subgrid
					if self.valid_location(grid,row,col,number):
						grid[row][col]=number
						if not self.find_empty_square(grid):
							self.counter+=1
							break
						else:
							if self.solve_puzzle(grid):
								return True
				break
		grid[row][col]=0  
		return False

	def generate_solution(self, grid):
		"""generates a full solution with backtracking"""
		number_list = [1,2,3,4,5,6,7,8,9]
		for i in range(0,81):
			row=i//9
			col=i%9
			#find next empty cell
			if grid[row][col]==0:
				shuffle(number_list)      
				for number in number_list:
					if self.valid_location(grid,row,col,number):
						self.path.append((number,row,col))
						grid[row][col]=number
						if not self.find_empty_square(grid):
							return True
						else:
							if self.generate_solution(grid):
								#if the grid is full
								return True
				break
		grid[row][col]=0  
		return False

	def get_non_empty_squares(self,grid):
		"""returns a shuffled list of non-empty squares in the puzzle"""
		non_empty_squares = []
		for i in range(len(grid)):
			for j in range(len(grid)):
				if grid[i][j] != 0:
					non_empty_squares.append((i,j))
		shuffle(non_empty_squares)
		return non_empty_squares
	
	def remove_numbers_from_grid(self):
		"""remove numbers from the grid to create the puzzle"""
		#get all non-empty squares from the grid
		non_empty_squares = self.get_non_empty_squares(self.grid)
		non_empty_squares_count = len(non_empty_squares)
		rounds = 3
		while rounds > 0 and non_empty_squares_count >= 17:
			#there should be at least 17 clues
			row,col = non_empty_squares.pop()
			non_empty_squares_count -= 1
			#might need to put the square value back if there is more than one solution
			removed_square = self.grid[row][col]
			self.grid[row][col]=0
			#make a copy of the grid to solve
			grid_copy = copy.deepcopy(self.grid)
			#initialize solutions counter to zero
			self.counter=0      
			self.solve_puzzle(grid_copy)   
			#if there is more than one solution, put the last removed cell back into the grid
			if self.counter!=1:
				self.grid[row][col]=removed_square
				non_empty_squares_count += 1
				rounds -=1
		return
def heuristic_solve_puzzle(board):
	sud = HillSudoku(board)
	maxScore = -1
	bestBoard = []
	for i in range(10):
		sud.reset()
		finalScore = sud.climbHill()
		maxFinalScore = max(finalScore)
		if(maxScore < maxFinalScore):
			maxScore = maxFinalScore
			bestBoard = sud.board.copy()
		if(maxFinalScore == 243):
			break
	return bestBoard

class HillSudoku():
	def __init__(self,hillBoard):
		self.fixed=self.convert(hillBoard)
		self.reset()

	def reset(self):
		self.board = (np.indices((9,9)) + 1)[1]
		for i in range(len(self.board)):
			self.board[i] = np.random.permutation(self.board[i])
		self.fixedValues = np.array(self.fixed)
		self.setup()

	def swapToPlace(self, val, line, col):
		valIndex = np.where(self.board[line]==val)[0][0]
		self.swap(self.board[line], valIndex, col)

	def setup(self):
		for (val, row, col) in self.fixedValues:
			self.swapToPlace(val, row, col)

	def fitness(self, board):
		score = 0
		rows, cols = board.shape
		for row in board:
			score += len(np.unique(row))
		for col in board.T:
			score += len(np.unique(col))
		for i in range(0, 3):
			for j in range(0, 3):
				sub = board[3*i:3*i+3, 3*j:3*j+3]
				score += len(np.unique(sub))
		return score

	def swap(self, arr, pos1, pos2):
		arr[pos1], arr[pos2] = arr[pos2], arr[pos1]

	def isFixed(self, row, col):
		for t in self.fixedValues:
			if(row == t[1] and col == t[2]):
				return True
		return False

	def bestNeighbor(self):
		tempBoard = self.board.copy()
		# best = (row, (col1, col2), val)
		# col1 va col2 swap voi nhau
		best = (0, (0,0), -1)
		for i in range(len(tempBoard)):
			for j in range(len(tempBoard[i])):
				for k in range(i,len(tempBoard)):
					if(self.isFixed(i,j) or self.isFixed(i,k)):
						continue
					self.swap(tempBoard[i], j, k)
					contestant = (i, (j,k), self.fitness(tempBoard))
					if(contestant[2] > best[2]):
						best = contestant
					#Thuc hien hoan doi co the su dung lai board
					self.swap(tempBoard[i], j, k)
		return best

	def climbHill(self):
		scores = []
		maxScore = self.fitness(self.board)
		# print("Initial score: " + str(maxScore))
		while True:
			# print("Current score: " + str(maxScore))
			scores.append(maxScore)
			(row, (col1, col2), nextScore) = self.bestNeighbor()
			if(nextScore <= maxScore):
				return scores
			self.swap(self.board[row], col1, col2)
			maxScore = nextScore
	def convert(self,hillBoard):
		afterconvert=[]
		for i in range(9):
			for j in range(9):
				if hillBoard[i][j]!=0:
					afterconvert.append((hillBoard[i][j],i,j))
		return afterconvert

class Grid:
	board = SudokuGenerator().grid
	state = board
	def __init__(self, rows, cols, width, height):
		self.rows = rows
		self.cols = cols
		self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
		self.width = width
		self.height = height
		self.model = None
		self.selected = None

	def update_model(self):
		self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

	def place(self, val):
		row, col = self.selected
		if self.cubes[row][col].value == 0:
			self.cubes[row][col].set(val)
			self.update_model()
			return True

	def sketch(self, val):
		row, col = self.selected
		self.cubes[row][col].set_temp(val)

	def draw(self, win):
		# Draw Grid Lines
		gap = self.width / 9
		for i in range(self.rows+1):
			if i % 3 == 0 and i != 0:
				thick = 4
			else:
				thick = 1
			pygame.draw.line(win, (0,0,0), (0, i*gap), (self.width, i*gap), thick)
			pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

		# Draw Cubes
		for i in range(self.rows):
			for j in range(self.cols):
				self.cubes[i][j].draw(win)

	def select(self, row, col):
		# Reset all other
		for i in range(self.rows):
			for j in range(self.cols):
				self.cubes[i][j].selected = False

		self.cubes[row][col].selected = True
		self.selected = (row, col)

	def clear(self):
		row, col = self.selected
		if self.state[row][col]==0:
			self.cubes[row][col].set(0)
			self.cubes[row][col].set_temp(0)
			self.update_model()

	def click(self, pos):
		"""
		:param: pos
		:return: (row, col)
		"""
		if pos[0] < self.width and pos[1] < self.height:
			gap = self.width / 9
			x = pos[0] // gap
			y = pos[1] // gap
			return (int(y),int(x))
		else:
			return None

	def is_finished(self):
		for i in range(self.rows):
			for j in range(self.cols):
				if self.cubes[i][j].value == 0:
					return False
		return True
	def new_puzzle(self,win):
		self.board = SudokuGenerator().grid
		
		self.state = self.board
		self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
		self.draw(win)
	def solve_puzzle(self,win):
		start_time=time.time()
		self.board = SudokuGenerator(grid=self.board).grid
		end_time=time.time()
		print("Time is %s \n"%(end_time-start_time))
		self.state = self.board
		self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
		self.draw(win)
	def heuristic_solve(self,win):
		start_time=time.time()
		self.board = heuristic_solve_puzzle(self.board)
		end_time=time.time()
		print("Time is %s \n"%(end_time-start_time))
		self.state = self.board
		self.cubes = [[Cube(self.board[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
		self.draw(win)

class Cube:
	rows = 9
	cols = 9

	def __init__(self, value, row, col, width ,height):
		self.value = value
		self.temp = 0
		self.row = row
		self.col = col
		self.width = width
		self.height = height
		self.selected = False

	def draw(self, win):
		fnt = pygame.font.SysFont("comicsans", 40)

		gap = self.width / 9
		x = self.col * gap
		y = self.row * gap

		if self.temp != 0 and self.value == 0:
			text = fnt.render(str(self.temp), 1, (128,128,128))
			win.blit(text, (x+5, y+5))
		elif self.value != 0:
			text = fnt.render(str(self.value), 1, (0, 0, 0))
			win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

		if self.selected:
			pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)
			

	def set(self, val):
		self.value = val

	def set_temp(self, val):
		self.temp = val

class button():
	def __init__(self, color, x,y,width,height, text=''):
		self.color = color
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.text = text

	def draw(self,win,outline=None):
		#Call this method to draw the button on the screen
		if outline:
			pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
			
		pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
		
		if self.text != '':
			font = pygame.font.SysFont('comicsans', 30)
			text = font.render(self.text, 1, (0,0,0))
			win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

	def isOver(self, pos):
		#Pos is the mouse position or a tuple of (x,y) coordinates
		if pos[0] > self.x and pos[0] < self.x + self.width:
			if pos[1] > self.y and pos[1] < self.y + self.height:
				return True
			
		return False
			   

def redraw_window(win, board):
	win.fill((255,255,255))
	# Draw grid and board
	new_puzzle.draw(win,(0,0,0))
	solve_puzzle.draw(win,(0,0,0))
	heuristic_solve.draw(win,(0,0,0))
	board.draw(win)

new_puzzle=button((0,255,0),380,560,150,35,"New Puzzle")
solve_puzzle=button((0,255,0),0,560,150,35,"Solve Puzzle")
heuristic_solve=button((0,255,0),200,560,150,35,"Heuristic Solve")
def main():
	win = pygame.display.set_mode((540,600))
	pygame.display.set_caption("Sudoku")
	board = Grid(9, 9, 540, 540)
	key = None
	run = True
	
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_1:
					key = 1
				if event.key == pygame.K_2:
					key = 2
				if event.key == pygame.K_3:
					key = 3
				if event.key == pygame.K_4:
					key = 4
				if event.key == pygame.K_5:
					key = 5
				if event.key == pygame.K_6:
					key = 6
				if event.key == pygame.K_7:
					key = 7
				if event.key == pygame.K_8:
					key = 8
				if event.key == pygame.K_9:
					key = 9
				if event.key == pygame.K_DELETE:
					board.clear()
					key = None
				if event.key == pygame.K_RETURN:
					i, j = board.selected
					if board.cubes[i][j].temp != 0:
						board.place(board.cubes[i][j].temp)
						key = None

						if board.is_finished():
							print("Game over")
							run = False

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				clicked = board.click(pos)
				if clicked:
					board.select(clicked[0], clicked[1])
					key = None
				if new_puzzle.isOver(pos):
					board.new_puzzle(win)
				if solve_puzzle.isOver(pos):
					board.solve_puzzle(win)
				if heuristic_solve.isOver(pos):
					board.heuristic_solve(win)
					
		if board.selected and key != None:
			board.sketch(key)

		redraw_window(win, board)
		pygame.display.update()


main()
pygame.quit()