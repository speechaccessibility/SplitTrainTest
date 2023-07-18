import unittest, json, update_train_test_split
import numpy as np
from gradescope_utils.autograder_utils.decorators import weight

# TestSequence
class TestStep(unittest.TestCase):
    @weight(1)
    def test_neighbors(self):
        # Generate all neighbors of a given simple assignment
        assignment = (('a','b','c'),('d',),('e','f'))
        neighborset = sorted([
            (('b','c','d'),('a',),('e','f')),
            (('a','c','d'),('b',),('e','f')),
            (('a','b','d'),('c',),('e','f')),
            (('b','c','e'),('d',),('a','f')),
            (('a','c','e'),('d',),('b','f')),
            (('a','b','e'),('d',),('c','f')),
            (('b','c','f'),('d',),('a','e')),
            (('a','c','f'),('d',),('b','e')),
            (('a','b','f'),('d',),('c','e')),
            (('a','b','c'),('e',),('d','f')),
            (('a','b','c'),('f',),('d','e'))
        ])
        print('Starting with len-%d neighborset'%(len(neighborset)))
        for n,nei in enumerate(update_train_test_split.neighbors(assignment)):
            self.assertIn(nei,neighborset,msg='%s not in %d tuples %s'%(nei,len(neighborset),neighborset))
            neighborset.remove(nei)
            print('Neighbor number %d: removed %s'%(n,nei))
        self.assertEqual(len(neighborset),0,msg='neighborset should be empty, not %s'%(neighborset))
