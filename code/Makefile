# Makefile for generating train/dev/test split of Speech Accessibility Project
# Usage: make current
# Mark Hasegawa-Johnson
# 8/24/2023
#

####################################################################################
# Splits for the main corpus
current: ../test_outputs/2023-08-23.json

../test_outputs/2023-08-23.json: SAPsplit.py
	-mkdir ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-07-20 ../test_outputs/2023-08-23.json 

../test_outputs/2023-07-20_split0.json: old/update_train_test_split.py
	-mkdir ../test_outputs
	python old/update_train_test_split.py -d ~/data/speechaccessibilityproject/SpeechAccessibility_2023-07-20 -p ../draft_standard/2023-06-08_split.json -b 10 -n 500 -o ../test_outputs/2023-07-20_split.json

../test_outputs/2023-06-08_split0.json: old/update_train_test_split.py
	-mkdir ../test_outputs
	python old/update_train_test_split.py -d ~/data/speechaccessibilityproject/2023-06-08 -b 10 -n 10 -o ../test_outputs/2023-06-08_split.json

####################################################################################
# Example splits generated at random

tmp/fake_data:
	mkdir -p tmp
	python generate_fake_data.py tmp/fake_data


####################################################################################
# Clean
clean:
	-rm ../test_outputs/*
	-rmdir ../test_outputs
	-rm -rf tmp
