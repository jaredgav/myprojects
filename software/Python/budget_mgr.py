# BUDGET MANAGER APP
# Implementatiom Phases
# PHASE 1
# Load in JSON and CSV formatted budget information then display basic metric (categorical amounts, total earnings, total out, total in)

# PHASE 2
# Add new expense
# Add new saving
 

# LATER PHASES
# Percentage of income view
# Amortizarion of loans

 # This program intends to provide the user a financial organizer and reports various ststistics and details. it also enables modifying values in the budget table to see how changes would affect the resr of the finances
# Command line arguments are available to load in a previous save
# the app will also have the ability to add additonal entries to the budget  

import sys
import os

class Expense(object):
	def __init__(self):
		self.title = "mortgage"
		self.category = "bill"
		self.budget_desired = 900
		self.budget_actual = 950
		self.monthly_occurance = 1
		self.additonal_attributes = "jsonString"
		
	def create_from_json(jsonObj):
		pass
	
	def create_from_csv(csvLine):
		""" Expects format
		title | category | desired | actual | occurance 
		"""
		tokens = csvLine.split(',')
		self.title = str(tokens[0])
		self.category = str(tokens[1])
		self.budget_desired = float(tokens[3])
		self.budget_actual = float(tokens[4])
		self.monthly_occurance = int(tokens[5])
		

class FileFormat(object):
	def __init__(self):
		self.UNKNOWN = 0
		self.JSON = 1
		self.CSV = 2
		self.CUSTOM = 3 # Jared created format

	def validate_file_format(file):
		""" Validates the file format, returns the file format
		"""
		# TODO
	


if __name__ == "__main__":
	
	# Flags
	# -fj specify file format is JSON
	# -fc specify file format is CSV
	# -ld loading a previous save from this app
	#
	# Args
	# 1. path to file
	# 2. ???
	
	# Parse input (using python parser library)
	
	# Import CSV/JSON/formated info file
	
	# Validate File Format - return format
	
	# Generate Report

	