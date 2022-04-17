# GUI.py
import pygame
from random import shuffle
import numpy as np
import copy
from solver import *
import time
pygame.font.init()

starImage=pygame.image.load('star.png')
starImageTransform=pygame.transform.scale(starImage,(50,50))
class SolveDFS:
	
	def __init__(self,board,n):
		self.board=board
		self.solution=[
        	[0,0,0,0,0],
        	[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0]
        	
    	]
		self.size=n
		self.solve_puzzle(n)

	def isAdjacent(self,row,col):
		for i in range(self.size):
			if self.solution[row][i]==1 or self.solution[i][col]==1:
				return True
		for i in range(self.size):
			for j in range(self.size):
				if self.board[i][j]==self.board[row][col]:
					if self.solution[i][j]==1:
						return True
		if row+1<=self.size-1 and col+1<=self.size-1:
			if self.solution[row+1][col+1]==1:
				return True
		if row+1<=self.size-1 and col-1>=0:
			if self.solution[row+1][col-1]==1:
				return True
		if row-1>=0 and col-1>=0:
			if self.solution[row-1][col-1]==1:
				return True
		if row-1>=0 and col+1<=self.size-1:
			if self.solution[row-1][col+1]==1:
				return True
		return False


	def solve_puzzle(self,n):
		if n==0:
			return True
		for i in range(0,self.size):
			for j in range(0,self.size):
				if not self.isAdjacent(i,j) and self.solution[i][j]!=1:
					self.solution[i][j]=1
					if self.solve_puzzle(n-1)==True:
						return True
					self.solution[i][j]=0
		return False

class SolveHeuristic:
	
	def __init__(self,board,n):
		self.board=board
		self.size=n
		self.solution=[
        	[0,0,0,0,0],
        	[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0]
    	]
		for i in range(self.size):
			self.solution[i][0]=1
		self.solution=self.heuristic_solve_puzzle()
	def setup(self):
		for i in range(self.size):
			shuffle(self.solution[i])
	def swap(self, arr, pos1, pos2):
		arr[pos1], arr[pos2] = arr[pos2], arr[pos1]
	def fitness(self,board):
		score=0
		for i in range(self.size):
			for j in range(self.size):
				if board[i][j]==1:
					score-=2
					for k in range(0,self.size):
						if board[i][k]==1:
							score+=1
					for k in range(0,self.size):
						if board[k][j]:
							score+=1
					if i+1<=self.size-1 and j+1<=self.size-1:
						if board[i+1][j+1]==1:
							score+=1
					if i+1<=self.size-1 and j-1>=0:
						if board[i+1][j-1]==1:
							score+=1
					if i-1>=0 and j-1>=0:
						if board[i-1][j-1]==1:
							score+=1
					if i-1>=0 and j+1<=self.size-1:
						if board[i-1][j+1]==1:
							score+=1
					score-=1
					for k in range(self.size):
						for l in range(self.size):
							if self.board[k][l]==self.board[i][j]:
								if board[k][l]==1:
									score+=1
		return int(score/2)
	def bestNeighbor(self):
		tempBoard=self.solution
		best =(0,(0,0),100)
		for i in range(5):
			for j in range(5):
				for k in range(i,5):
					if tempBoard[i][j]==1:
						self.swap(tempBoard[i], j, k)
						contestant = (i, (j,k), self.fitness(tempBoard))
						if(contestant[2] < best[2]):
							best = contestant
							#Thuc hien hoan doi co the su dung lai board
						self.swap(tempBoard[i], j, k)
		return best
	def climbHill(self):
		scores = []
		maxScore = self.fitness(self.solution)
		# print("Initial score: " + str(maxScore))
		while True:
			# print("Current score: " + str(maxScore))
			scores.append(maxScore)
			(row, (col1, col2), nextScore) = self.bestNeighbor()
			if(nextScore >= maxScore):
				return scores
			self.swap(self.solution[row], col1, col2)
			maxScore = nextScore
	def heuristic_solve_puzzle(self):
		maxScore = 100
		bestBoard = []
		for i in range(10):
			self.setup()
			finalScore = self.climbHill()
			maxFinalScore = min(finalScore)
			if(maxScore > maxFinalScore):
				maxScore = maxFinalScore
				bestBoard = self.solution
			if(maxFinalScore == 0):
				break
		print(maxFinalScore)
		return bestBoard

class Grid:
	solution=[
        [0,0,0,0,0],
        	[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0],
			[0,0,0,0,0]
    ]
	board = [
        [0,0,1,2,2],
        [0,0,1,2,3],
		[0,0,1,4,3],
		[4,4,4,4,3],
		[4,4,4,4,3]
    ]
	def __init__(self, rows, cols, width, height):
		self.rows = rows
		self.cols = cols
		self.cubes = [[Shape(0, i, j, width, height) for j in range(cols)] for i in range(rows)]
		self.width = width
		self.height = height
		self.model = None
		self.selected = None

	def update_model(self):
		self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

	def place(self):
		row, col = self.selected
		if self.cubes[row][col].value == 0:
			self.cubes[row][col].set(1)
			self.update_model()
			return True
		if self.cubes[row][col].value == 1:
			self.cubes[row][col].set(0)
			self.update_model()
			return True

	def sketch(self, val):
		row, col = self.selected
		self.cubes[row][col].set_temp(val)

	def draw(self, win):
		# Draw Grid Lines
		gap = self.width / 5
		h=self.height/5
		pygame.draw.line(win, (0, 0, 0), (0,self.height), (self.width,self.height), 4)
		
		for i in range(self.rows):
			for j in range(self.cols):
				if j<self.cols-1:
					if self.board[i][j]!=self.board[i][j+1]:
						thick=4
					else:
						thick=1
					
					pygame.draw.line(win, (0, 0, 0), ((j+1) * gap, i*gap), ((j+1) * gap, i*gap+h), thick)
				if j<self.cols-1:
					if self.board[j][i]!=self.board[j+1][i]:
						thick_row=4
					else:
						thick_row=1
					pygame.draw.line(win, (0,0,0), (i*gap, (j+1)*gap), (i*gap+gap, (j+1)*gap), thick_row)
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
			gap = self.width / 5
			x = pos[0] // gap
			y = pos[1] // gap
			return (int(y),int(x))
		else:
			return None

	def is_finished(self):
		pass
	def new_puzzle(self,win):
		pass
	def solve_puzzle(self,win):
		#time right here
		start_time=time.time()
		self.solution = SolveDFS(self.board,5).solution
		end_time=time.time()
		print("Time is %s \n"%(end_time-start_time))
		self.cubes = [[Shape(self.solution[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
		self.draw(win)
	def heuristic_solve(self,win):
		start_time=time.time()
		self.solution = SolveHeuristic(self.board,5).solution
		end_time=time.time()
		print("Time is %s \n"%(end_time-start_time))
		self.cubes = [[Shape(self.solution[i][j], i, j, self.width, self.height) for j in range(self.cols)] for i in range(self.rows)]
		self.draw(win)

class Shape:
	rows = 5
	cols = 5

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

		gap = self.width / 5
		x = self.col * gap
		y = self.row * gap
		if self.value!=0:
			win.blit(starImageTransform, (x + (gap/2 - starImageTransform.get_width()/2), y + (gap/2 - starImageTransform.get_height()/2)))
		if self.selected:
			pygame.draw.rect(win, (255,0,0), (x,y, gap ,gap), 3)
			#win.blit(starImageTransform, (x + (gap/2 - starImageTransform.get_width()/2), y + (gap/2 - starImageTransform.get_height()/2)))

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
	board = Grid(5, 5, 540, 540)
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
					board.place()
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