import numpy as np
import time
import curses

class MatrixFight():

	def __init__(self, screen, height=10, width=10, groups=3):
		self.screen = screen
		self.height = height
		self.width = width
		self.groups = list(range(1, groups+1, 1))

		self.strategys = {1:"m", 2:"r", 3:"h"}

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
		fields = {i : 0 for i in self.groups+ [0]}
		army = {i : 0 for i in self.groups+ [0]}
		self.screen.clear()
		for idx, row in enumerate(self.matrix):
			#line = ""
			for idx2, v in enumerate(row):
				armyStrength = self.strenghts[idx,idx2]
				line = "{}   ".format(armyStrength)
				fields[v] += 1
				army[v] += armyStrength

				self.screen.addstr(idx, idx2*4, line, curses.color_pair(v*20))
		fieldStr, armyStr = "Fields: ", "Army: "
		for f in sorted(fields):
			fieldStr += "{}: {} ".format(f, fields[f])
		for f in sorted(army):
			armyStr += "{}: {} ".format(f, army[f])

		self.screen.addstr(11,0, fieldStr)
		self.screen.addstr(12, 0, armyStr)
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
			winPercentage = min(max((s1-s2)*0.1+0.5, 0), 1)
			diceRoll = np.random.random_integers(10)
			if diceRoll <= winPercentage * 10:
				winner = p1
			else:
				winner = p2
			#self.screen.addstr(15,0, "S1 {} S2{} Perc {} Dice {}".format(s1, s2, winPercentage, diceRoll))
			#self.screen.refresh()
			#time.sleep(2)
		return winner

	def nextRound(self, speed=0.005):
		for group in self.groups:
			self.executeTurn(group)
			self.printMatrix()
			time.sleep(speed)

	def executeTurn(self, group):
		attacker, defender = self.chooseTurn(group)

		if attacker is not None and defender is not None:
			winner = self.fight(attacker, defender)
			if winner == attacker:
				self.matrix[defender] = group
				self.strenghts[defender] = min(self.strenghts[winner] + 1, 9)
				self.strenghts[winner] = 1
			else:
				self.strenghts[attacker] = max(self.strenghts[attacker] - 1, 1)

	def chooseTurn(self, group):
		if self.strategys[group] == "r":
			return self.randomTurn(group)
		elif self.strategys[group] == "h":
			return self.highLowTurn(group)
		else:
			return self.maxArmyTurn(group)


	def possibleActions(self, group):
		posAttacker = [tuple(x) for x in np.argwhere(self.matrix == group)]
		posTargets = {}
		if len(posAttacker) > 0:
			posTargets = {x: self.getNeighbours(*x) for x in posAttacker}
			# delete all neighbours from same group
			posTargets = {n: [x for x in posTargets[n] if self.matrix[x] != group] for n in
			              posTargets}

			for n in list(posTargets):
				if posTargets[n] == []:
					posTargets.pop(n)
		return posTargets

	def randomTurn(self, group):
		attacker, defender = None, None
		posTargets = self.possibleActions(group)
		if len(posTargets) > 0:
			# choose random attacker with possible targets
			posAttackers = [x for x in posTargets if len(posTargets[x]) > 0]
			chosenId = np.random.choice(len(posAttackers))
			attacker = tuple(posAttackers[chosenId])

			# let it choose a random target
			defender = posTargets[attacker][np.random.choice(len(posTargets[attacker]))]

		return attacker, defender

	def highLowTurn(self, group):
		attacker, defender = None, None
		posTargets = self.possibleActions(group)
		if len(posTargets) > 0:
			# choose attacker with best army
			posAttackers = [(x, self.strenghts[x]) for x in posTargets if len(posTargets[x]) > 0]
			attacker = tuple(sorted(posAttackers, key=lambda x:x[1])[-1][0])
			#attacker = tuple(posAttackers[chosenId])

			# let it choose a target with lowest army
			posDefenders = [(x,self.strenghts[x]) for x in posTargets[attacker]]
			defender = tuple(sorted(posDefenders, key=lambda x: x[1])[0][0])
			#defender = posTargets[attacker][chosenId]

		return attacker, defender

	def maxArmyTurn(self, group):
		attacker, defender = None, None
		posTargets = self.possibleActions(group)
		if len(posTargets) > 0:
			# choose attacker with best army
			posAttackers = [(x, self.strenghts[x]) for x in posTargets if len(posTargets[x]) > 0 and self.strenghts[x] < 9]
			# if all are maxed
			if len(posAttackers) == 0:
				posAttackers = [(x, self.strenghts[x]) for x in posTargets if
				                len(posTargets[x]) > 0]

			attacker = tuple(sorted(posAttackers, key=lambda x: x[1])[-1][0])
			# attacker = tuple(posAttackers[chosenId])

			# let it choose a target with lowest army
			posDefenders = [(x, self.strenghts[x]) for x in posTargets[attacker]]
			defender = tuple(sorted(posDefenders, key=lambda x: x[1])[0][0])
		# defender = posTargets[attacker][chosenId]

		return attacker, defender



def main(stdscr=False):
	curses.start_color()
	curses.use_default_colors()

	for i in range(0, curses.COLORS):
		curses.init_pair(i + 1, i, -1)

	env = MatrixFight(stdscr)
	for i in range(20000):
		env.nextRound()


if __name__ == "__main__":
	curses.wrapper(main)