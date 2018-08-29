##############################################################################
##############################################################################
## Template file for problem 1. You have to fill in two functions BELOW 	##
## Both take in input n = number of sides in the die 						##
## 																			##
## 1. findSumDieRoll(n)	: Return expected value of sum 						##
## 2. findNumberOfRolls(n)  : Return expected value of number of rolls 		##
## 																		 	##
## For both, you only have to fill in the math function where indicated     ##
##                                                                          ##
## You can run this template file to see the output of your functions       ##
## for a 6 sided die.														## 
## Simply run: `python problem1_template.py`                            	##
## You should see the output printed once your program runs.                ##
##                                                                          ##
## DO NOT CHANGE ANYTHING ELSE BELOW. ONLY FILL IN THE LOGIC.      			##
##                                                                          ##
## Good Luck!                                                               ##
##############################################################################
##############################################################################


def findSumDieRoll(n):
	##################################
	##          FILL ME IN          ##
	##################################

	sumRolls = n/2 # Replace me with your answer

	return sumRolls

def findNumberOfRolls(n):
	##################################
	##          FILL ME IN          ##
	##################################
	
	numRolls = n/2	# Replace me with your answer

	return numRolls

if __name__ == "__main__":
	numberOfSides = 6
	print('For a %i-sided die, expected value of sum: %i and number of rolls: %i'%(numberOfSides\
		, findSumDieRoll(numberOfSides), findNumberOfRolls(numberOfSides)))