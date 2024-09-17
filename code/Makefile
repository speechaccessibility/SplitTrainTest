# Makefile for generating train/dev/test split of Speech Accessibility Project
# Usage:
#  make current - make a split for the current dataset (uses files outside this directory)
#  make test - run regression tests, and make a split for tmp/fake_data
#
# Mark Hasegawa-Johnson
# 8/24/2023
# Modified 1/17/2024
#

previous=2024-07-31
current=2024-08-31

####################################################################################
# Splits for the main corpus
../test_outputs/SpeechAccessibility_$(current)_Split.json: SAPsplit.py ../lists/contributor_lists_$(current).xlsx
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/data/SpeechAccessibility_$(current) ../test_outputs/SpeechAccessibility_$(current)_Split.json -c ../test_outputs/SpeechAccessibility_$(current)_Split_by_Contributors.json -L ../lists/contributor_lists_$(current).xlsx -l logs/SpeechAccessibility_$(current)_Split.log

####################################################################################3
# make_zipfiles
# Purpose:
#   Arrange files into train, dev, and test subdirectories
make_zipfiles:
	mkdir -p  ~/data/speechaccessibilityproject/SpeechAccessibility_$(current)_zips
	python make_zipfiles.py ~/data/speechaccessibilityproject/SpeechAccessibility_$(current)_traindev  ~/data/speechaccessibilityproject/SpeechAccessibility_$(current)_zips

####################################################################################3
# Test overlaps
# Purpose:
#   This is a quality control check on the created list.
#   It compares the most recent list to the current list, and generates a report
#   specifying any insertions, deletions, or substitutions.
#   Generally speaking, from one month to the next, we hope that there will be
#   many insertions, few if any substitutions, and few if any deletions.
test_overlaps:
	python test_overlaps.py  ../test_outputs/SpeechAccessibility_$(previous)_Split.json ../test_outputs/SpeechAccessibility_$(current)_Split.json logs/test_overlaps_$(current).json > logs/test_overlaps_$(current).log

####################################################################################
# Example splits generated at random
# Call: `make test`
# Purpose:
#   This runs some unit tests on the programs SAPsplit.py and promptfiles.py.
#
test: tmp/fake_data tmp/fake_split.json
	python runtests.py

tmp/fake_split.json: tmp/fake_data
	python SAPSplit.py tmp/fake_data tmp/fake_split.json -c tmp/contributor_split.json

tmp/fake_data:
	mkdir -p tmp
	python generate_fake_data.py tmp/fake_data


####################################################################################
# Clean
# Call: `make clean`
# Purpose:
#   Delete temporary files and temporary directories.
clean:
	-rm ../test_outputs/*
	-rmdir ../test_outputs
	-rm -rf tmp
	-rm -rf PromptsAnnotationGuidelines
	-rm test_overlaps.json
