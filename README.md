# Standard Train/Dev/Test Split for the Speech Accessibility Project

This repository contains the code used to create the train/dev/test split for each release of the Speech Accessibility Corpus.

* transcripts: This directory contains transcripts for the train and dev splits of publicly released portions of the corpus.

* code: SAPsplit.py generates JSON files.  arrange_files.py creates train, dev, and test directories, and puts contributors into the appropriate directories, preparatory to distribution.

* lists: This directory provides excel files mapping from contributor to promptlist.  These files are necessary as input to SAPsplit.py.

