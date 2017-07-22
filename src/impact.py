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
    confidence = 0.2
    
    def __init__(self, change_history):
        self.change_history = change_history
        
        
    def rules_from_1_to_n_minus_1(self, commit, trans_type):
        changes_from_1_to_n_minus_1 = self.change_history.changes_before_commit(commit, trans_type)
        return self.compute_assoc_rules(changes_from_1_to_n_minus_1, self.support, self.confidence)
    
    def recommendations_at(self, commit, trans_type):
        changes_at_n = self.change_history.changes_at_commit(commit, trans_type)
        rules_from_1_to_n_minus_1 = self.rules_from_1_to_n_minus_1(commit, trans_type)
        
        return self.match_recommentdations(changes_at_n, rules_from_1_to_n_minus_1)
    
    def match_recommentdations(self, changes_at_n, rules):
        match_recommentdations = []
        for specific_change in changes_at_n:
            elements_to_evaluate = self.elements_to_evaluate(specific_change)
            match_recommentdations.append(self.match_recommentdation(elements_to_evaluate, rules))
        return match_recommentdations
    
    def match_recommentdation(self, elements_to_evaluate, rules):
        if len(elements_to_evaluate) == 1:
            return []
        
        correct_rec = []
        for rule in rules:
            rule_from = rule[0]
            rule_to = rule[1]
            for element in elements_to_evaluate:
                element_from = element[0]
                element_to = element[1]
                # If True, this a correct recommendation
                if element_from in rule_from and element_to in rule_to:
                    correct_rec.append(element)
        return correct_rec
    
    def elements_to_evaluate(self, changes):
        elements_to_evaluate = []
        for change_from in changes:
            for change_to in changes:
                if change_from != change_to:
                    elements_to_evaluate.append([change_from, change_to])
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
                one_to_one_rules.append(rule)
        return one_to_one_rules
        
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

change_history = read_changes("../apimining_test")
rec = Recommender(change_history)
result = rec.recommendations_at("5", "added")
print result
