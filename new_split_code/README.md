# Code that creates SAPC2 Train/Dev/Test1/Test2 Splits

The program <a href="split_sapc2_data.py">split_sapc2_data.py</a>
reads in the splits from SAPC1, and the current research distribution
of the Speech Accessibility Project, and creates a data split for
SAPC2 (the second Speech Accessibility Project Challenge).  The
program <a href="reader.py">reader.py</a> reads and writes a few file
manifest and JSON formats, and <a href="test.py">test.py</a> tests the
code.

It's designed to satisfy a few constraints:

1. All speakers that were part of any split in SAPC1 must be placed in the train 
or dev splits of SAPC2.

2. Any speaker that was in the train or dev splits of any research
distribution should be in train or dev, respectively, of SAPC2.

3. There must be at most 875 in train and 124 in dev, including the maximum
possible number from the minimum group.

4. From the speakers in SAPC test1 and test2, the test utterances
will include only utterances whose text transcription is not identical to
any utterance spoken by a speaker in any train or dev distribution.
