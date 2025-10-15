# Code that creates SAPC2 Train/Dev/Test1/Test2 Splits

The program <a href="split_sapc2_data.py">split_sapc2_data.py</a>
reads in the splits from SAPC1, and the current research distribution
of the Speech Accessibility Project, and creates a data split for
SAPC2 (the second Speech Accessibility Project Challenge).  The
program <a href="reader.py">reader.py</a> reads and writes a few file
manifest and JSON formats, and <a href="test.py">test.py</a> tests the
code.

It's designed to satisfy a few constraints:

1. **All speakers that were part of any split in SAPC1** (train, dev,
test1, or test2) must be placed in the train or dev splits of SAPC2.
The purpose of this rule is to allow us to publish the SAPC1 test
corpora openly, so that researchers who were not part of SAPC1 in 2025
will be able, in the future, to demonstrate algorithm innovations that
outperform the best SAPC1 competition results.

2. **Any speaker that was in the train or dev splits of any research
distribution** should be in train or dev, respectively, of SAPC2.  The
purpose of this rule is to make sure that none of the SAPC2 competing
teams have access to extra SAP data beyond what's provided by the
competition.

3. There must be **at most 875 in train and 124 in dev**, including the
maximum possible number from the minimum group.  The purpose of this
rule is to make it possible for most organizations in most of the
countries of the world to participate in SAPC2, if they wish to do so,
without running afoul of United States Department of Justice biometric
data export regulations.

4. From the speakers in SAPC test1 and test2, the test utterances will
include **only utterances whose text transcription is not identical to
any utterance in any train or dev distribution**.
The purpose of this rule is to prevent any trained ASR from winning
the competition by simply memorizing sentences that were spoken by
somebody in the training set.