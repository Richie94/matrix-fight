import numpy as np
import time
import curses

class MatrixFight():

	def __init__(self, screen, height=10, width=10, groups=3):
		self.screen = screen
		self.height = height
		self.width = width
		self.groups = list(range(1, groups+1, 1))

		self.rounds = 0

		self.createMatrix()

	def createMatrix(self):
		self.matrix = np.zeros((self.width, self.height), dtype=np.int)
		self.strenghts = np.zeros((self.width, self.height), dtype=np.int)

		x = np.random.choice(self.width, 1)
		y = np.random.choice(self.height, 1)
		for group in self.groups:
			while self.matrix[x,y] != 0:
				x = np.random.choice(self.width, 1)
				y = np.random.choice(self.height, 1)
			self.matrix[x,y] = group
			self.strenghts[x, y] = 1

	def printMatrix(self):
		self.screen.clear()
		for idx, row in enumerate(self.matrix):
			#line = ""
			for idx2, v in enumerate(row):
				line = "{}-{} ".format(v, self.strenghts[idx,idx2])

				self.screen.addstr(idx, idx2*4, line, curses.color_pair(v*20))
		self.screen.refresh()

	def getNeighbours(self, x, y):
		neighbours= []
		if x < self.width-1:
			neighbours.append((x+1, y))
		if x > 0:
			neighbours.append(((x-1,y)))
		if y < self.height-1:
			neighbours.append((x, y+1))
		if y > 0:
			neighbours.append((x,y-1))

		return neighbours

	def fight(self, p1, p2):
		# with each point difference 20% more chance to kill it
		s1 = self.strenghts[p1]
		s2 = self.strenghts[p2]

		if s1 == 0:
			winner = p2
		elif s2 == 0:
			winner = p1
		else:
			# calculate chance for s1 to win
			winPercentage = min(max((s1-s2)*0.2, 0), 1)
			diceRoll = np.random.random_integers(10)
			if diceRoll <= winPercentage * 10:
				winner = p1
			else:
				winner = p2
		return winner

	def nextRound(self):
		for group in self.groups:
			self.executeTurn(group)
			self.printMatrix()
			time.sleep(.2)

	def executeTurn(self, group):
		attacker, defender = self.randomTurn(group)

		if attacker is not None and defender is not None:
			winner = self.fight(attacker, defender)
			if winner == attacker:
				self.matrix[defender] = group
				self.strenghts[defender] = min(self.strenghts[winner] + 1, 9)
				self.strenghts[winner] = 1
			else:
				self.strenghts[attacker] = max(self.strenghts[attacker] - 1, 1)


	def randomTurn(self, group):
		attacker, defender = None, None
		groupMembers = [tuple(x) for x in np.argwhere(self.matrix==group)]
		if len(groupMembers) > 0:
			memberNeighbours = {x : self.getNeighbours(*x) for x in groupMembers}
			# delete all neighbours from same group
			memberNeighbours = {n : [x for x in memberNeighbours[n] if self.matrix[x] != group] for n in memberNeighbours}
			# choose members with existing border
			outerMembers = [idx for idx in groupMembers if len(memberNeighbours[idx]) > 0]
			chosenId = np.random.choice(len(outerMembers))
			attacker = tuple(outerMembers[chosenId])

			# 2. let it choose a random neighbour from other group
			defender = memberNeighbours[attacker][np.random.choice(len(memberNeighbours[attacker]))]

		return attacker, defender


def main(stdscr=False):
	curses.start_color()
	curses.use_default_colors()

	for i in range(0, curses.COLORS):
		curses.init_pair(i + 1, i, -1)

	env = MatrixFight(stdscr)
	for i in range(2000):
		env.nextRound()
		#time.sleep(1)


if __name__ == "__main__":
	curses.wrapper(main)
	#main()