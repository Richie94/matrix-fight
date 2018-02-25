# matrix-fight
Started little Minigame where i want to test different AIs later.

Game works like this:
You start in a Grid. Every Team starts with one soldier. 
You can Attack Neighbour Cells. If you win, your soldier move to the field where you won and gain one experience (up to maximum of 9). On the old field a new soldier has been born with one experience. Fights with other soldiers work like this: if one has 5 more experience, he wins. Else for every point of difference the more experienced soldier has 10% more chance to win. If an attacker fails his attack, he looses one xp.

So far simple included strategys:
- random
- attack everytime with most experienced the less experienced (idea: win fight)
- attack everytime with most experienced below maximum experience (idea: win fight/ max experience)
