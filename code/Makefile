# Makefile for generating train/dev/test split of Speech Accessibility Project
# Usage:
#  make current - make a split for the current dataset (uses files outside this directory)
#  make test - run regression tests, and make a split for tmp/fake_data
#
# Mark Hasegawa-Johnson
# 8/24/2023
# Modified 1/17/2024
#

previous=2024-01-31
current=2024-02-29

####################################################################################
# Splits for the main corpus
../test_outputs/SpeechAccessibility_$(current)_Split.json: SAPsplit.py ../lists/contributor_lists_$(current).xlsx
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_$(current) ../test_outputs/SpeechAccessibility_$(current)_Split.json -c ../test_outputs/SpeechAccessibility_$(current)_Split_by_Contributors.json -L ../lists/contributor_lists_$(current).xlsx -l logs/SpeechAccessibility_$(current)_Split.log

../test_outputs/SpeechAccessibility_2023-11-30_Split.json: SAPsplit.py PromptsAnnotationGuidelines/commands_b1_b10_PD.txt
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-11-30 ../test_outputs/SpeechAccessibility_2023-11-30_Split.json -c ../test_outputs/SpeechAccessibility_2023-11-30_Split_by_Contributors.json

../test_outputs/SpeechAccessibility_2023-10-31_Split.json: SAPsplit.py
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-10-31 ../test_outputs/SpeechAccessibility_2023-10-31_Split.json -c ../test_outputs/SpeechAccessibility_2023-10-31_Split_by_Contributors.json

../test_outputs/SpeechAccessibility_2023-10-05_Split.json: SAPsplit.py
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-10-05 ../test_outputs/SpeechAccessibility_2023-10-05_Split.json -c ../test_outputs/SpeechAccessibility_2023-10-05_Split_by_Contributors.json

../test_outputs/SpeechAccessibility_2023-08-31_Split.json: SAPsplit.py
	mkdir -p ../test_outputs
	python SAPSplit.py ~/data/speechaccessibilityproject/SpeechAccessibility_2023-08-31 ../test_outputs/SpeechAccessibility_2023-08-31_Split.json -c ../test_outputs/SpeechAccessibility_2023-08-31_Split_by_Contributors.json

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
# Required prompt lists -- deprecated
# Call: `make PromptsAnnotationGuidelines/commands_b1_b10_PD.txt`
# Purpose:
#  Before we had a separate report on the list to which each contributor is assigned,
#  SAPsplit.py tried to guess each contributor's list by comparing their recorded
#  prompt texts to the texts in these lists.  This method does not generalize to
#  the case of multiple etiologies, so it was abandoned 2023-12-31 in favor of a
#  separate report file, ../lists/contributor_lists_$(current).xlsx, that maps from contributor uuid
#  to list number.
PromptsAnnotationGuidelines/commands_b1_b10_PD.txt:
	git clone https://github.com/speechaccessibility/PromptsAnnotationGuidelines

####################################################################################3
# Test overlaps
# Call: `make logs/test_overlaps_2023-12-31.json` (or whatever is current)
# Purpose:
#   This is a quality control check on the created list.
#   It compares the most recent list to the current list, and generates a report
#   specifying any insertions, deletions, or substitutions.
#   Generally speaking, from one month to the next, we hope that there will be
#   many insertions, few if any substitutions, and few if any deletions.
logs/test_overlaps_$(current).json:
	python test_overlaps.py  ../draft_standard/SpeechAccessibility_$(previous)_Split.json ../test_outputs/SpeechAccessibility_$(current)_Split.json logs/test_overlaps_$(current).json > logs/test_overlaps_$(current).log

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
