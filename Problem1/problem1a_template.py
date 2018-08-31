##################################################################################
##################################################################################
## Template file for problem 1. 						##
## First, fill in your answer logic below		                        ##
##################################################################################
#                                LOGIC GOES BELOW                    		 #
##################################################################################
#
#
#
#
#
##################################################################################
##################################################################################
## You have to fill in two functions BELOW 		                        ##
## Both take in input n 	                                                ##
## 					                                        ##
## 1. findSum(n)	    : Return expected value of sum  			##
## 2. findNumber(n)  : Return expected value of number        	       	        ##
## 										##									    ##
## For both, you only have to fill in the math function where indicated     	##
## 										##									    ##
## You can run this template file to see the output of your functions       	##
## for n=6.         								##						    ##
## Simply run: `python problem1_template.py`                            	##
## You should see the output printed once your program runs.                	##
##                                                                          	##
## DO NOT CHANGE ANYTHING ELSE BELOW. ONLY FILL IN THE LOGIC.      		##
##                                                                          	##
## Good Luck!                                                               	##
##################################################################################
##################################################################################


def findSum(n):
	##################################
	##          FILL ME IN          ##
	##################################
	sumR = n/2 # Replace me with your answer

	return round(sumR, 2)

def findNumber(n):
	##################################
	##          FILL ME IN          ##
	##################################
	numR = n/2	# Replace me with your answer

	return round(numR, 2)

if __name__ == "__main__":
	inputN = 6
	sumR = findSum(inputN)
	numR = findNumber(inputN)
	print('For input n=%i, expected value of sum: %.2f and number: %.2f'%(inputN, sumR, numR))
