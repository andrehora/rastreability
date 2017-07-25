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
            if not self.removed:
                return []
            removed = map(lambda each: "R-"+each, self.removed)
            added = map(lambda each: "A-"+each, self.added)
            return removed + added
    
class ChangeHistory:
    
    def __init__(self, changes):
        self.changes = changes
        self.distinct_commits = self.remove_duplicates(self.commits())
        
    def changes_at_commit(self, commit, trans_type):
        changes_at_commit = filter(lambda each: each.commit == commit, self.changes)
        changes_at_commit = map(lambda each: each.transaction_for_type(trans_type), changes_at_commit)
        return filter(lambda each: len(each)>0, changes_at_commit)
    
    def changes_before_commit(self, commit, trans_type, change_types):
        changes_before = []
        for change in self.changes:
            if change.commit == commit:
                return changes_before
            trans = change.transaction_for_type(trans_type)
            if trans and change.change_type in change_types:
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
    
    def __init__(self, support, confidence, change_history, transaction_type, change_types):
        self.change_history = change_history
        self.trans_type = transaction_type
        self.change_types = change_types
        self.support = support
        self.confidence = confidence
        
    def recommendations_at(self, commit):
        changes_at_n = self.change_history.changes_at_commit(commit, self.trans_type)
        changes_from_1_to_n_minus_1 = self.change_history.changes_before_commit(commit, self.trans_type, self.change_types)
        #print len(changes_from_1_to_n_minus_1)
        
        rules_from_1_to_n_minus_1 = self.compute_assoc_rules(changes_from_1_to_n_minus_1, self.support, self.confidence)
        return self.match_recommendations(changes_at_n, rules_from_1_to_n_minus_1)
    
    def match_recommendations(self, changes_at_n, rules):
        result = []
        for single_elements in changes_at_n:
            #print single_elements
            rec = Recommendation(single_elements, rules)
            elements_to_evaluate = self.find_elements_to_evaluate(single_elements)
            if elements_to_evaluate:
                rec = self.match_elements_and_recommendation(single_elements, elements_to_evaluate, rec, result)
                #if rec:
                    #result.append(rec)
        return result
    
    def match_elements_and_recommendation(self, single_elements, elements_to_evaluate, recommendation, result):
        #matches = []
        for element in single_elements:
            matcher = self.match_elements(element, recommendation, elements_to_evaluate, result)
            #if matcher:
                #result.append(matcher)
        #return matches
    
    def match_elements(self, element_from, recommendation, elements_to_evaluate, result):
        #result = []
        rules = recommendation.recommendation_for(element_from)
        for rule in rules:
            if self.match_left_and_right(rule, elements_to_evaluate):
                result.append((rule.__str__(), True))
            else: result.append((rule.__str__(), False))
        #return result
    
    def match_left_and_right(self, rule, elements_to_evaluate):
        if [rule.left, rule.right] in elements_to_evaluate:
            return True
        return False
    
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
                left = list(rule[0])[0]
                right = list(rule[1])[0]
                if self.trans_type == "evolution":
                    if left.startswith("R-") and right.startswith("A-"):
                        assoc_rule = AssocRule(left, right, rule[2], rule[3])
                        one_to_one_rules.append(assoc_rule)
                else: 
                    assoc_rule = AssocRule(left, right, rule[2], rule[3])
                    one_to_one_rules.append(assoc_rule)
        return one_to_one_rules

class Recommendation:
    
    def __init__(self, elements, rules):
        self.elements = elements
        self.rules = rules
        self.rec = {}
        self.compute_recommendation()
        self.sort_recommendation()
        
    def recommendation_for(self, element):
        if element in self.rec:
            return self.rec[element]
        return []

    def compute_recommendation(self):
        for rule in self.rules:
            if rule.left in self.elements:
                self.ensure_recommendation(rule.left, rule)
                
    def sort_recommendation(self):
        for key in self.rec:
            rules = self.rec[key]
            sorted_rules = sorted(rules, key=lambda rule: rule.confidence, reverse=True)
            self.rec[key] = sorted_rules[0:10]
            
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
            
            if removed_list or added_list:
                change = Change(commit, change_type, removed_list, added_list)
                changes.append(change)
    
    return ChangeHistory(changes)

class RecomendationResult:
    
    def __init__(self):
        self.all_result = []
        self.all_correct_recommendation = []
        self.all_incorrect_recommendation = []
    
    def update(self, result):
        self.result = result
        self.correct_recommendation = filter(lambda each: each[1], result)
        self.incorrect_recommendation = filter(lambda each: not each[1], result)
        
        self.all_result.extend(result)
        self.all_correct_recommendation.extend(self.correct_recommendation)
        self.all_incorrect_recommendation.extend(self.incorrect_recommendation)
        
    def count_recommendation(self):
        return len(self.result)
    
    def count_correct_recommendation(self):
        return len(self.correct_recommendation)
    
    def count_incorrect_recommendation(self):
        return len(self.incorrect_recommendation)
    
    def count_all_recommendation(self):
        return len(self.all_result)
    
    def count_all_correct_recommendation(self):
        return len(self.all_correct_recommendation)
    
    def count_all_incorrect_recommendation(self):
        return len(self.all_incorrect_recommendation)

def run(path, transaction_type, supp, conf):
    
    change_history = read_changes(path)
    
    rec_tracked = Recommender(supp, conf, change_history, transaction_type, ["SameMethod"])
    rec_tracked_and_untracked = Recommender(supp, conf, change_history, transaction_type, ["SameMethod", "RenameMethod", "MoveMethod"])
    
    result_tracked = RecomendationResult()
    result_tracked_and_untracked = RecomendationResult()
    
    for commit in change_history.distinct_commits:
        
        r = rec_tracked.recommendations_at(commit)
        
        result_tracked.update(r)
        c_tracked = result_tracked.count_correct_recommendation()
        i_tracked = result_tracked.count_incorrect_recommendation()
        ac_tracked = result_tracked.count_all_correct_recommendation()
        ai_tracked = result_tracked.count_all_incorrect_recommendation()
        
        r = rec_tracked_and_untracked.recommendations_at(commit)
        result_tracked_and_untracked.update(r)
        c_tracked_and_untracked = result_tracked_and_untracked.count_correct_recommendation()
        i_tracked_and_untracked = result_tracked_and_untracked.count_incorrect_recommendation()
        ac_tracked_and_untracked = result_tracked_and_untracked.count_all_correct_recommendation()
        ai_tracked_and_untracked = result_tracked_and_untracked.count_all_incorrect_recommendation()
        
        #print r
        print commit
        print c_tracked, i_tracked, ac_tracked, ai_tracked
        print c_tracked_and_untracked, i_tracked_and_untracked, ac_tracked_and_untracked, ai_tracked_and_untracked

run("../apimining2_che", "added", 2, 0.5)
#run("../apimining2_MPAndroidChart", "removed")

# transactions = (('a', 'b'), ('a', 'b'), ('a', 'b', 'c'), ('b'))
# relim_input = itemmining.get_relim_input(transactions)
# item_sets = itemmining.relim(relim_input, min_support=1)
# rules = assocrules.mine_assoc_rules(item_sets, min_support=1, min_confidence=0.1)
# print rules