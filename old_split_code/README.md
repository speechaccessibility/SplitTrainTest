# Standard Train/Dev/Test Split for the Speech Accessibility Project

This repository contains the code used to create the train/dev/test split for each release of the Speech Accessibility Corpus.

* code: SAPsplit.py generates JSON files.  arrange_files.py creates train, dev, and test directories, and puts contributors into the appropriate directories, preparatory to distribution.  make_zipfiles.py zips the train and dev directories into 7z files, each of which has a maximum size of 20G.  Makefile automates some of these tasks.

* lists: This directory provides excel files mapping from contributor to promptlist.  These files are necessary as input to SAPsplit.py.

Unfortunately, it is not yet possible for researchers to create the train/dev/test split on your own unless the file lists/contributor_lists_$(current).xlsx has already been created for you.  Creating that file requires annotator authorization.  If that file exists, it should be possible for you to re-create the splits on your own.

