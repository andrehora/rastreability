from pymining import itemmining, assocrules

class Change:
    def __init__(self, commit, change_type, removed, added):
        self.commit = commit
        self.change_type = change_type
        self.removed = removed
        self.added = added
        
    def transaction_for_type(self, trans_type):
        if trans_type == "removed":
            return self.removed
        
        if trans_type == "added":
            return self.added
        
        if trans_type == "evolution":
            pass
    
class ChangeHistory:
    
    def __init__(self, changes):
        self.changes = changes
        self.distinct_commits = self.remove_duplicates(self.commits())
        
    def changes_at_commit(self, commit, trans_type):
        changes_at_commit = filter(lambda each: each.commit == commit, self.changes)
        return map(lambda each: each.transaction_for_type(trans_type), changes_at_commit)
    
    def changes_before_commit(self, commit, trans_type):
        changes_before = []
        for change in self.changes:
            if change.commit == commit:
                return changes_before
            trans = change.transaction_for_type(trans_type)
            changes_before.append(trans)
        return changes_before
        
    def commits(self):
        return map(lambda each: each.commit, self.changes)
    
    def remove_duplicates(self, elements):
        #TODO, a kind of ordered set
        ordered = []
        for each in elements:
            if each not in ordered:
                ordered.append(each)
        return ordered
    
class Recommender:
    
    support = 2
    confidence = 0.20
    
    def __init__(self, change_history):
        self.change_history = change_history
        
        
    def rules_from_1_to_n_minus_1(self, commit, trans_type):
        changes_from_1_to_n_minus_1 = self.change_history.changes_before_commit(commit, trans_type)
        return self.compute_assoc_rules(changes_from_1_to_n_minus_1, self.support, self.confidence)
    
    def recommendations_at(self, commit, trans_type):
        
        changes_at_n = self.change_history.changes_at_commit(commit, trans_type)
        rules_from_1_to_n_minus_1 = self.rules_from_1_to_n_minus_1(commit, trans_type)
        
        return self.match_recommendations(changes_at_n, rules_from_1_to_n_minus_1)
    
    def match_recommendations(self, changes_at_n, rules):
        match_recommentdations = []
        for elements in changes_at_n:
            rec = Recommendation(elements, rules)
            elements_to_evaluate = self.find_elements_to_evaluate(elements)
            if elements_to_evaluate:
                rec = self.match_elements_and_recommendation(elements_to_evaluate, rec)
                if rec:
                    match_recommentdations.append(rec)
        return match_recommentdations
    
    def match_elements_and_recommendation(self, elements_to_evaluate, recommendation):
        matches = []
        for element in elements_to_evaluate:
            element_from = element[0]
            element_to = element[1]
            matcher = self.match_element(element_from, element_to, recommendation)
            if matcher:
                matches.append(matcher)
        return matches
    
    def match_element(self, element_from, element_to, recommendation):
        rules = recommendation.recommendation_for(element_from)
        #Correct recommendation
        for rule in rules:
            if element_from == rule.left and element_to == rule.right:
                return [element_from, element_to]
        #Incorrect recommendation
        for rule in rules:
            if element_from == rule.left and not element_to == rule.right:
                return ["N"]
        #No recommendation
        return []
            
    def find_elements_to_evaluate(self, elements):
        if len(elements) == 1:
            #TODO
            return [elements[0], elements[0]]
        elements_to_evaluate = []
        for element_from in elements:
            for element_to in elements:
                if element_from != element_to:
                    elements_to_evaluate.append([element_from, element_to])
        return elements_to_evaluate
    
    def compute_assoc_rules(self, trans, supp, conf):
        relim_input = itemmining.get_relim_input(trans)
        item_sets = itemmining.relim(relim_input, min_support=supp)
        rules = assocrules.mine_assoc_rules(item_sets, min_support=supp, min_confidence=conf)
        return self.filter_one_to_one_rules(rules)
    
    def filter_one_to_one_rules(self, rules):
        one_to_one_rules = []
        for rule in rules:
            if len(rule[0]) == 1 and len(rule[1]) == 1:
                #TODO
                assoc_rule = AssocRule(list(rule[0])[0], list(rule[1])[0], rule[2], rule[3])
                one_to_one_rules.append(assoc_rule)
        return one_to_one_rules

class Recommendation:
    
    def __init__(self, elements, rules):
        self.elements = elements
        self.rules = rules
        self.rec = {}
        self.compute_recommendation()
        
    def recommendation_for(self, element):
        if element in self.rec:
            return self.rec[element]
        return []

    def compute_recommendation(self):
        for rule in self.rules:
            if rule.left in self.elements:
                self.ensure_recommendation(rule.left, rule)
    
    def ensure_recommendation(self, key, rule):
        if key in self.rec:
            recs = self.rec[key]
            recs.append(rule)
            self.rec[key] = recs
        else: self.rec[key] = [rule]
        
    def __str__(self):
        s = ""
        for key in self.rec:
            s += "Element: " + key + "\n"
            for rule in self.rec[key]:
                s += rule.__str__() + "\n"
        return s
    
class AssocRule:
    
    def __init__(self, left, right, support, confidence):
        self.left = left
        self.right = right
        self.support = support
        self.confidence = confidence
        
    def __str__(self):
        return self.left + " -> " + self.right + " " + str(self.support) + " " + str(self.confidence)
        
def string_to_list(s_list):
    s_list = s_list[1:-1].replace(" ", "")
    l_list = s_list.split(",")
    if not l_list[0]:
        l_list = []
    return l_list
    
def read_changes(path):
    changes = []
    with open(path) as f:
        for line in f:
            change_type = line.split(";")[0].rstrip()
            commit = line.split(";")[1].rstrip()
            removed = line.split(";")[2].rstrip()
            added = line.split(";")[3].rstrip()
            
            removed_list = string_to_list(removed)
            added_list = string_to_list(added)
               
            change = Change(commit, change_type, removed_list, added_list)
            changes.append(change)
    
    return ChangeHistory(changes)

#change_history = read_changes("../apimining2_che")
change_history = read_changes("../apimining_test")
rec = Recommender(change_history)
#result = rec.recommendations_at("f2047ea01aaeddbd4a0fc9865b435d0ccb40ffe1", "added")
result = rec.recommendations_at("10", "added")
print result
