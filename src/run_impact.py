import impact

def run_and_export(path, transaction_type, supp, conf):
    
    export_file_name = path + "-" + transaction_type + "-" + str(supp) + "-" + str(conf)
    out_file = open(export_file_name, 'w')
    
    print>>out_file, path
    print>>out_file, transaction_type
    print>>out_file, "Support:", supp
    print>>out_file, "Confidence:", conf
    
    change_history = impact.read_changes(path)
    rec_tracked = impact.Recommender(supp, conf, change_history, transaction_type, ["SameMethod"])
    rec_tracked_and_untracked = impact.Recommender(supp, conf, change_history, transaction_type, ["SameMethod", "RenameMethod", "MoveMethod"])
    
    result_tracked = impact.RecomendationResult()
    result_tracked_and_untracked = impact.RecomendationResult()
    
    for commit in change_history.distinct_commits:
        
        r = rec_tracked.recommendations_at(commit)
        result_tracked.update(r)
        c_tracked = result_tracked.count_correct_recommendation()
        i_tracked = result_tracked.count_incorrect_recommendation()
        ac_tracked = result_tracked.count_all_correct_recommendation()
        ai_tracked = result_tracked.count_all_incorrect_recommendation()
        prec_tracked = result_tracked.precision()
        
        r = rec_tracked_and_untracked.recommendations_at(commit)
        result_tracked_and_untracked.update(r)
        c_tracked_and_untracked = result_tracked_and_untracked.count_correct_recommendation()
        i_tracked_and_untracked = result_tracked_and_untracked.count_incorrect_recommendation()
        ac_tracked_and_untracked = result_tracked_and_untracked.count_all_correct_recommendation()
        ai_tracked_and_untracked = result_tracked_and_untracked.count_all_incorrect_recommendation()
        prec_tracked_and_untracked = result_tracked_and_untracked.precision()
        
        precision_gain = 0
        recall_gain = 0
        if prec_tracked:
            precision_gain = round(float(prec_tracked_and_untracked)/prec_tracked,2)
        if ac_tracked:
            recall_gain = round(float(ac_tracked_and_untracked)/ac_tracked,2)
        
        print>>out_file,"Commit:", commit
        print>>out_file,"Tracked:", c_tracked, i_tracked, ac_tracked, ai_tracked, prec_tracked
        print>>out_file,"Tracked+Untracked:", c_tracked_and_untracked, i_tracked_and_untracked, ac_tracked_and_untracked, ai_tracked_and_untracked, prec_tracked_and_untracked
        print>>out_file,"Precision gain:", precision_gain
        print>>out_file, "Recall gain:", recall_gain


#system = "che"
system = "fresco"
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
#system = "spring-framework"
system_path = "../apimining2_"+system

run_and_export(system_path, "added", 1, 0.1)
run_and_export(system_path, "added", 1, 0.9)
run_and_export(system_path, "added", 3, 0.1)
run_and_export(system_path, "added", 3, 0.9)

run_and_export(system_path, "evolution", 1, 0.1)
run_and_export(system_path, "evolution", 1, 0.9)
run_and_export(system_path, "evolution", 3, 0.1)
run_and_export(system_path, "evolution", 3, 0.9)