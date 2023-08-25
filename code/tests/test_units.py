import unittest, os, json, random, glob
import promptfiles, SAPsplit, generate_fake_data

# TestSequence
class TestStep(unittest.TestCase):
    def setUp(self):
        self.datadir = 'tmp/fake_data'
        if not os.path.isdir(self.datadir):
            generate_fake_data.main(self.datadir)
        self.corpus = SAPsplit.load_corpus(self.datadir)
        self.prompts, self.novel_sentences = promptfiles.load_PD_prompts()

    def test_load_corpus(self):
        subdirs = os.listdir(self.datadir)
        self.assertEqual(len(subdirs),len(self.corpus),
                         msg='corpus length is %d, should be %d'%(len(self.corpus),len(subdirs)))
        subdir = random.choice(subdirs)
        self.assertIn(subdir,self.corpus,msg='%s should be in corpus but is not'%(subdir))
        jsonfiles = glob.glob(os.path.join(self.datadir, subdir, '*.json'))
        with open(jsonfiles[0]) as f:
            contributor = json.load(f)
        utt = random.choice(contributor['Files'])
        nhits = 0
        for file in self.corpus[subdir]['Files']:
            if file['Filename']==utt['Filename']:
                nhits += 1
                self.assertEqual(file['Prompt']['Prompt Text'],utt['Prompt']['Prompt Text'],
                                 msg='%s prompt incorrect: %s'%(file['Filename'],
                                                                file['Prompt']['Prompt Text']))
        self.assertGreater(nhits,0,msg='%s not loaded from %s'%(utt['Filename'],subdir))
            
    def test_create_subset2prompts(self):
        subset2prompts = SAPsplit.create_subset2prompts(self.prompts, self.novel_sentences)
        allprompts = set.union(subset2prompts['train'],subset2prompts['dev'],subset2prompts['test'])
        for id in self.corpus:
            for file in self.corpus[id]['Files']:
                prompt = file['Prompt']['Prompt Text']
                if file['Prompt']['Category Description']=="Spontaneous Speech Prompts":
                    self.assertNotIn(prompt,allprompts,
                                     msg='prompt is spontaneous: %s'%(prompt))
                elif file['Prompt']['Category Description']=="Digital Assistant Commands":
                    self.assertIn(prompt,allprompts,
                                  msg='prompt should be included:%s'%(prompt))
                else:
                    pass

    def test_assign_contributors(self):
        subset2prompts = SAPsplit.create_subset2prompts(self.prompts, self.novel_sentences)
        subset2contributors,subset2wavfiles,wavfile2prompt=SAPsplit.assign_contributors(subset2prompts,self.corpus)
        allcontributors = [ c for s in ['train','dev','test'] for c in subset2contributors[s] ]
        self.assertEqual(len(self.corpus),len(allcontributors),
                         msg='subset2contributors has %d! (%d)'%(len(allcontributors),len(self.corpus)))
        for c in self.corpus:
            self.assertIn(c,allcontributors,msg='%s missing from subset2contributors'%(c))
        wavfiles = set([ w for s in ['train','dev','test'] for w in subset2wavfiles[s] ])
        utts = set([ utt['Filename'] for data in self.corpus.values() for utt in data['Files'] ])
        w2p = set(wavfile2prompt.keys())
        for utt in utts:
            self.assertIn(utt,wavfiles,msg='subset2wavefiles missing %s'%(utt))
            self.assertIn(utt,w2p,msg='wavfile2prompt missing %s'%(utt))
        for wavfile in wavfiles:
            self.assertIn(wavfile,utts,msg='corpus is missing %s'%(wavfile))
            self.assertIn(wavfile,w2p,msg='wavfile2prompt missing %s'%(wavfile))
        for wavfile in w2p:
            self.assertIn(wavfile,wavfiles,msg='subset2wavfiles is missing %s'%(wavfile))
            self.assertIn(wavfile,utts,msg='corpus missing %s'%(wavfile))
        

    def test_determine_sharing(self):
        subset2prompts = SAPsplit.create_subset2prompts(self.prompts, self.novel_sentences)
        subset2contributors,subset2wavfiles,wavfile2prompt=SAPsplit.assign_contributors(subset2prompts,self.corpus)
        subset2files = SAPsplit.determine_sharing(subset2wavfiles, wavfile2prompt)
        bothdev = set.union(set(subset2files['dev']['shared'].keys()),
                            set(subset2files['dev']['unshared'].keys()))
        bothtest = set.union(set(subset2files['test']['shared'].keys()),
                             set(subset2files['test']['unshared'].keys()))
        for id in self.corpus:
            if id in subset2contributors['train']:
                self.assertNotIn(id,subset2contributors['dev'],msg='%s in train and dev'%(id))
                self.assertNotIn(id,subset2contributors['test'],msg='%s in train and test'%(id))
                for utt in self.corpus[id]['Files']:
                    self.assertIn(utt['Filename'],subset2files['train'],
                                  msg='%s should be in subset2files["train"]'%(utt['Filename']))
            elif id in subset2contributors['dev']:
                self.assertNotIn(id,subset2contributors['test'],msg='%s in dev and test'%(id))
                for utt in self.corpus[id]['Files']:
                    self.assertIn(utt['Filename'],bothdev,
                                  msg='%s should be in subset2files["dev"]'%(utt['Filename']))
            else:
                for utt in self.corpus[id]['Files']:
                    self.assertIn(utt['Filename'],bothtest,
                                  msg='%s should be in subset2files["test"]'%(utt['Filename']))
                
