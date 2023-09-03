# Makefile for generating train/dev/test split of Speech Accessibility Project
# Usage:
#  make current - make a split for the current dataset (uses files outside this directory)
#  make test - run regression tests, and make a split for tmp/fake_data
#
# Mark Hasegawa-Johnson
# 8/24/2023
#

####################################################################################
# Splits for the main corpus
current: ../test_outputs/SpeechAccessibility_2023-08-31_Split.json

../test_outputs/SpeechAccessibility_2023-08-31_Split.json: SAPsplit.py
	-mkdir ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-08-31 ../test_outputs/SpeechAccessibility_2023-08-31_Split.json -c ../test_output/SpeechAccessibility_2023-08-23_Split_by_Contributors.json

../test_outputs/2023-08-23.json: SAPsplit.py
	-mkdir ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-07-20 ../test_outputs/2023-08-23_waveformsplit.json -c ../test_output/2023-08-23_contributorsplit.json

../test_outputs/2023-07-20_split0.json: old/update_train_test_split.py
	-mkdir ../test_outputs
	python old/update_train_test_split.py -d ~/data/speechaccessibilityproject/SpeechAccessibility_2023-07-20 -p ../draft_standard/2023-06-08_split.json -b 10 -n 500 -o ../test_outputs/2023-07-20_split.json

../test_outputs/2023-06-08_split0.json: old/update_train_test_split.py
	-mkdir ../test_outputs
	python old/update_train_test_split.py -d ~/data/speechaccessibilityproject/2023-06-08 -b 10 -n 10 -o ../test_outputs/2023-06-08_split.json

####################################################################################
# Example splits generated at random

test: tmp/fake_data tmp/fake_split.json
	python runtests.py

tmp/fake_split.json: tmp/fake_data
	python SAPSplit.py tmp/fake_data tmp/fake_split.json -c tmp/contributor_split.json

tmp/fake_data:
	mkdir -p tmp
	python generate_fake_data.py tmp/fake_data


####################################################################################
# Clean
clean:
	-rm ../test_outputs/*
	-rmdir ../test_outputs
	-rm -rf tmp
