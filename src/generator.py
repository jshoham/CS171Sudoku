#generator

import grid

inputFile = 'gen_input.txt'
outputFile = 'gen_output.txt'


def readfile(inputFile):
	f = open(inputFile, 'r')
	line = f.readline().split()
	if len(line) == 4:
		N, p, q, M = line
	else:
		print "input error"
		
#generate a puzzle

def generate(N, p, q, M):
	for x in range(M):
		assign(grid)

