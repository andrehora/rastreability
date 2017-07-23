import unittest, impact

class Sample:
    
    def recommender(self):
        change_history = impact.read_changes("../apimining_test")
        rec = impact.Recommender(change_history, "added")
        rec.support = 1
        rec.confidence = 0.1
        return rec

class TestSample(unittest.TestCase):
    
    def setUp(self):
        self.rec = Sample().recommender()
        
    def test_iter_1(self):
        #SameMethod;1;[];[A, B]
        rec = self.rec.recommendations_at("1")
        self.assertEqual(len(rec), 0)
        
    def test_iter_2(self):
        #SameMethod;2;[];[A, B, C]
        rec = self.rec.recommendations_at("2")
        self.assertEqual(len(rec), 1)
        changes = rec[0]
        self.assertEqual(len(changes), 2)
        change1 = changes[0][0]
        self.assertEqual(change1, ('A -> B 1 1.0', True))
        change2 = changes[1][0]
        self.assertEqual(change2, ('B -> A 1 1.0', True))
        
    def test_iter_3_1(self):
        #RenameMethod;3;[];[A, B, C]
        rec = self.rec.recommendations_at("3")
        self.assertEqual(len(rec), 2)
        changes = rec[0]
        self.assertEqual(len(changes), 2)
        change = changes[0][0]
        self.assertEqual(change, ('A -> C 1 0.5', False))
        change = changes[0][1]
        self.assertEqual(change, ('A -> B 2 1.0', True))
        change = changes[1][0]
        self.assertEqual(change, ('B -> C 1 0.5', False))
        change = changes[1][1]
        self.assertEqual(change, ('B -> A 2 1.0', True))
    
    def test_iter_3_2(self):
        #RenameMethod;3;[];[A, B, C]
        rec = self.rec.recommendations_at("3")
        self.assertEqual(len(rec), 2)
        changes = rec[1]
        self.assertEqual(len(changes), 1)
        change = changes[0][0]
        self.assertEqual(change, ('A -> C 1 0.5', False))
        change = changes[0][1]
        self.assertEqual(change, ('A -> B 2 1.0', False))
        
    def test_iter_4(self):
        #RenameMethod;4;[];[A, C]
        rec = self.rec.recommendations_at("4")
        self.assertEqual(len(rec), 1)
        changes = rec[0]
        self.assertEqual(len(changes), 2)
        change = changes[0][0]
        self.assertEqual(change, ('A -> K 1 0.25', False))
        change = changes[0][1]
        self.assertEqual(change, ('A -> C 1 0.25', True))
        change = changes[0][2]
        self.assertEqual(change, ('A -> B 3 0.75', False))
        change = changes[1][0]
        self.assertEqual(change, ('C -> B 1 1.0', False))
        change = changes[1][1]
        self.assertEqual(change, ('C -> A 1 1.0', True))
        
    def test_iter_5(self):
        #RenameMethod;5;[];[Z]
        rec = self.rec.recommendations_at("5")
        self.assertEqual(len(rec), 0)
        
    def test_iter_6(self):
        #RenameMethod;6;[];[X,Y]
        rec = self.rec.recommendations_at("6")
        self.assertEqual(len(rec), 0)
        
    def test_iter_7(self):
        #SameMethod;7;[];[]
        rec = self.rec.recommendations_at("7")
        self.assertEqual(len(rec), 0)
    
    def test_iter_8(self):
        #RenameMethod;8;[];[X,Y]
        rec = self.rec.recommendations_at("8")
        self.assertEqual(len(rec), 1)
        changes = rec[0]
        self.assertEqual(len(changes), 2)
        change = changes[0][0]
        self.assertEqual(change, ('X -> Y 1 1.0', True))
        change = changes[1][0]
        self.assertEqual(change, ('Y -> X 1 1.0', True))
        
    def test_iter_9(self):
        #RenameMethod;9;[];[Z]
        rec = self.rec.recommendations_at("9")
        self.assertEqual(len(rec), 0)
        
if __name__ == '__main__':
    unittest.main()