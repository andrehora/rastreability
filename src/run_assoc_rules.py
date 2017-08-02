import impact

def pretty_rules(rules):
    out = ""
    for rule in rules:
        out += rule.__str__() + ", "
    return out

def run_and_export(path, out_file, transaction_type, supp, conf):
    
    print>>out_file, transaction_type
    print>>out_file, "Support:", supp
    print>>out_file, "Confidence:", conf
    
    change_history = impact.read_changes(path)
    tracked_setup = impact.Recommender(supp, conf, change_history, transaction_type, ["SameMethod"])
    tracked_and_untracked_setup = impact.Recommender(supp, conf, change_history, transaction_type, ["SameMethod", "RenameMethod", "MoveMethod"])
    
    tracked_rules = tracked_setup.run_assoc_rules()
    tracked_and_untracked_rules = tracked_and_untracked_setup.run_assoc_rules()
    
    exclusive_tracked_rules = set(tracked_rules) - set(tracked_and_untracked_rules)
    exclusive_tracked_and_untracked_rules = set(tracked_and_untracked_rules) - set(tracked_rules)
    
    print "Tracked rules: " + pretty_rules(tracked_rules)
    print "Tracked & untracked rules: " + pretty_rules(tracked_and_untracked_rules)
    #print "New rules: " + pretty_rules(new_rules)
    print len(exclusive_tracked_rules)
    print len(exclusive_tracked_and_untracked_rules)
    
    len_tracked_rules = len(set(tracked_rules))
    len_tracked_and_untracked_rules = len(set(tracked_and_untracked_rules))
    absolute_improvement = len_tracked_and_untracked_rules - len_tracked_rules
    relative_improvement = round(float(len_tracked_and_untracked_rules)/len_tracked_rules,2)
    print str(len_tracked_rules), str(len_tracked_and_untracked_rules), absolute_improvement, relative_improvement

#system = "che"
#system = "fresco"
#system = "guava"
#system = "clojure"
#system = "storm"
#system = "MPAndroidChart"
#system = "glide"
#system = "guice"
#system = "retrofit"
#system = "okhttp"
#system = "RxJava"
#system = "Android-Universal-Image-Loader"
#system = "elasticsearch"
#system = "kotlin"
system = "spring-framework"

system_path = "../apimining2_"+system

transaction_type = "added"
export_file_name = system_path + "_assoc_rules_" + transaction_type
out_file = open(export_file_name, 'w')

run_and_export(system_path, out_file, transaction_type, 1, 0.1)
run_and_export(system_path, out_file, transaction_type, 1, 0.9)
run_and_export(system_path, out_file, transaction_type, 3, 0.1)
run_and_export(system_path, out_file, transaction_type, 3, 0.9)

transaction_type = "evolution"
export_file_name = system_path + "_assoc_rules_" + transaction_type
out_file = open(export_file_name, 'w')

run_and_export(system_path, out_file, transaction_type, 1, 0.1)
run_and_export(system_path, out_file, transaction_type, 1, 0.9)
run_and_export(system_path, out_file, transaction_type, 3, 0.1)
run_and_export(system_path, out_file, transaction_type, 3, 0.9)