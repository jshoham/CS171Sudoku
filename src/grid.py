# grid
from random import randint

class Grid(object):
	
	def __init__(self, N=9, p=3, q=3):
		self.N = N		# The number of tokens
		self.p = p		# The number of rows per block
		self.q = q		# The number of columns per block
		self.grid = [[[x for x in xrange(N)] for i in xrange(N)] for j in xrange(N)]
		
	def display(self):
		width = len(str(self.N))+1
		rowSeperator = '+'.join(['-'*(width*self.q)]*self.p)
		
		for row in range(self.N):
			if row%self.p == 0 and row != 0: print rowSeperator
			
			line = ''
			for cell in range(self.N):
				if cell%self.q == 0 and cell != 0: line += '|'
				
				cellValues = self.grid[row][cell]
				if len(cellValues) == 1 and cellValues[0] != 0:
					line += str(cellValues[0]).center(width)
				else:
					line += '.'.center(width)
				
			print line
	
	def randomFill(self):
		for i in range(self.N):
			for j in range(self.N):
				randomValue = randint(0, self.N)
				self.grid[i][j]= [randomValue]
				
	def clear(self):
		for i in range(self.N):
			for j in range(self.N):
				del self.grid[i][j][:]