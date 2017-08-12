import dateutil.parser, collections, networkx as nx
from __builtin__ import True
from Carbon.Aliases import true

class ModelUtil:
    
    def count_relations(self, relations):
        names = map(lambda relation: relation.name, relations)
        c = collections.Counter(names)
        return sorted(c.items())
    
    def trackeds_class_level(self, relations):
        result = filter(lambda relation: relation.tracked() and relation.class_level(), relations)
        return map(lambda each: each.name, result)
    
    def trackeds_method_level(self, relations):
        result = filter(lambda relation: relation.tracked() and relation.method_level(), relations)
        return map(lambda non_refactoring: non_refactoring.name, result)
    
    def untrackeds_class_level(self, relations):
        result = filter(lambda relation: relation.untracked() and relation.class_level(), relations)
        return map(lambda each: each.name, result)
    
    def untrackeds_method_level(self, relations):
        result = filter(lambda relation: relation.untracked() and relation.method_level(), relations)
        return map(lambda non_refactoring: non_refactoring.name, result)
    
    def trackeds(self, relations):
        result = filter(lambda relation: relation.not_refactoring(), relations)
        return map(lambda each: each.name, result)
    
    def untrackeds(self, relations):
        result = filter(lambda relation: relation.is_refactoring(), relations)
        return map(lambda each: each.name, result)
    
    def matchings(self, relations):
        result = filter(lambda relation: relation.is_matching(), relations)
        return map(lambda each: each.name, result)
    
    def non_matchings(self, relations):
        result = filter(lambda relation: relation.non_matching(), relations)
        return map(lambda each: each.name, result)

class ModelHistory:
    
    path_element_separator = ">"
    
    def __init__(self, model_path, include_change=False, include_matching=False, 
                 include_nonmatching=False):
        self.entities = {}
        self.relations = []
        self.versions = {}
        self.alternative_names = {}
        self.include_change = include_change
        self.include_matching = include_matching
        self.include_nonmatching = include_nonmatching
        self.create_model(model_path)
        
    def select_random(self):
        from random import randint
        for each in range(0,15):
            random_id = randint(1, len(self.relations))
            print self.relations[random_id].full_name()
        
    def relations_with_roots(self):
        return filter(lambda relation: relation.is_root(), self.relations)
    
    def relations_without_refactorings(self):
        return filter(lambda relation: relation.with_change(), self.relations)
    
    def relations_with_matching_refactorings(self):
        return filter(lambda relation: relation.with_matching(), self.relations)
    
    def relations_with_nonmatching_refactorings(self):
        return filter(lambda relation: relation.with_nonmatching(), self.relations)
        
    
    def count_relations(self):
        return ModelUtil().count_relations(self.relations)
    
    def trackeds_class_level(self):
        return ModelUtil().trackeds_class_level(self.relations)
    
    def trackeds_method_level(self):
        return ModelUtil().trackeds_method_level(self.relations)
    
    def untrackeds_class_level(self):
        return ModelUtil().untrackeds_class_level(self.relations)
    
    def untrackeds_method_level(self):
        return ModelUtil().untrackeds_method_level(self.relations)
    
    def trackeds(self):
        return ModelUtil().trackeds(self.relations)
    
    def untrackeds(self):
        return ModelUtil().untrackeds(self.relations)
    
    def matchings(self):
        return ModelUtil().matchings(self.relations)
    
    def non_matchings(self):
        return ModelUtil().non_matchings(self.relations)
    
    def ratio_of_tracked(self):
        number_of_relations = len(self.relations)
        number_of_tracked = len(self.trackeds())
        return round(number_of_tracked/float(number_of_relations),2)
    
    def ratio_of_untracked(self):
        number_of_relations = len(self.relations)
        number_of_untracked = len(self.untrackeds())
        return round(number_of_untracked/float(number_of_relations),2)
    
    def ratio_of_tracked_class_level(self):
        number_of_tracked = len(self.trackeds())
        number_of_trackeds_class_level = len(self.trackeds_class_level())
        return round(number_of_trackeds_class_level/float(number_of_tracked),2)
    
    def ratio_of_tracked_method_level(self):
        number_of_tracked = len(self.trackeds())
        number_of_trackeds_method_level = len(self.trackeds_method_level())
        return round(number_of_trackeds_method_level/float(number_of_tracked),2)
    
    def ratio_of_untracked_class_level(self):
        number_of_untracked = len(self.untrackeds())
        number_of_untrackeds_class_level = len(self.untrackeds_class_level())
        return round(number_of_untrackeds_class_level/float(number_of_untracked),2)
    
    def ratio_of_untracked_method_level(self):
        number_of_untracked = len(self.untrackeds())
        number_of_untrackeds_method_level = len(self.untrackeds_method_level())
        return round(number_of_untrackeds_method_level/float(number_of_untracked),2)
    
    def ratio_of_matching(self):
        number_of_untracked = len(self.untrackeds())
        number_of_matching = len(self.matchings())
        return round(number_of_matching/float(number_of_untracked),2)
    
    def ratio_of_non_matching(self):
        number_of_untracked = len(self.untrackeds())
        number_of_non_matching = len(self.non_matchings())
        return round(number_of_non_matching/float(number_of_untracked),2)
        
    def sorted_versions(self):
        return sorted(self.versions.values(), key=lambda version: version.date)
        
    def list_entities(self):
        return self.entities.values()
    
    def ensure_entity(self, node):
        if node in self.entities:
            return self.entities[node]
        e = Entity(node)
        self.entities[node] = e
        return e
    
    def ensure_version(self, commit, date):
        if commit in self.versions:
            return self.versions[commit]
        v = Version(commit, date)
        self.versions[commit] = v
        return v
    
    def pretty_node_name(self, key, cont, relation_name):
        separator = ">"
        return key + separator + str(cont) + self.path_element_separator + relation_name
    
    def ensure_alternative_name(self, key, relation_name):
        if key in self.alternative_names:
            value = self.alternative_names[key]
            cont = value[0]
            cont = cont + 1
            self.alternative_names[key] = (cont, relation_name)
            return self.pretty_node_name(key, cont, relation_name)
        initial_count = 1
        self.alternative_names[key] = (initial_count, relation_name)
        return self.pretty_node_name(key, initial_count, relation_name)
    
    def get_alternative_name(self, key, relation_name):
        if key in self.alternative_names:
            cont, relation_name = self.alternative_names[key]
            return self.pretty_node_name(key, cont, relation_name)
        initial_count = 1
        self.alternative_names[key] = (initial_count, relation_name)
        return self.pretty_node_name(key, initial_count, relation_name)
    
    def resolve_alternative_names(self, relation):

        name1 = relation.entity1.name
        alternative_name = self.get_alternative_name(name1, relation.name)
        relation.alternative_name1 = alternative_name
            
        name2 = relation.entity2.name
        alternative_name = self.ensure_alternative_name(name2, relation.name)
        relation.alternative_name2 = alternative_name
        
    def create_entities_and_relations(self, relation, node1, node2, commit, date):
        
        #Refactor this code later
        include_relation = False
        rel = SimpleRelation(relation)
        
        if self.include_change and rel.is_change():
            include_relation = True
        elif self.include_matching and rel.is_matching():
            include_relation = True
        elif self.include_nonmatching and rel.non_matching():
            include_relation = True
        
        if include_relation:
            e1 = self.ensure_entity(node1)
            e2 = self.ensure_entity(node2)
            r = Relation(relation, commit, e1, e2)
            self.resolve_alternative_names(r)
            self.relations.append(r)
                
            v = self.ensure_version(commit, date)
            v.relations.append(r)
        
    def create_model(self, model_history):
        with open(model_history) as f:
            for line in f:
                relation = line.split(";")[0].rstrip()
                code_change = line.split(";")[1].rstrip()
                node1 = line.split(";")[2].rstrip()
                node2 = line.split(";")[3].rstrip()
                commit = line.split(";")[4].rstrip()
                date = line.split(";")[5].rstrip()
                date = dateutil.parser.parse(date)
                self.create_entities_and_relations(relation, node1, node2, commit, date)
                
    def __str__(self):
        
        number_of_versions = len(self.versions)
        number_of_relations = len(self.relations)
        
        number_of_tracked = len(self.trackeds())
        number_of_tracked_class_level = len(self.trackeds_class_level())
        number_of_tracked_method_level = len(self.trackeds_method_level())
        
        number_of_untracked = len(self.untrackeds())
        number_of_untracked_class_level = len(self.untrackeds_class_level())
        number_of_untracked_method_level = len(self.untrackeds_method_level())
        
        number_of_matching = len(self.matchings())
        number_of_non_matching = len(self.non_matchings())
        
#         s = ""
#         s += "Commits: "   + str(number_of_versions) + " "
#         s += "Changes: "        + str(number_of_relations) + " "
#         s += "Tracked: "    + str(number_of_tracked) + \
#             " ("            + str(self.ratio_of_tracked()) + ") "
#         s += "- Class: "    + str(number_of_tracked_class_level) + \
#             " ("            + str(self.ratio_of_tracked_class_level()) + ") "
#         s += "Method: "   + str(number_of_tracked_method_level) + \
#             " ("            + str(self.ratio_of_tracked_method_level()) + ") "
#         s += "Untracked: "  + str(number_of_untracked) + \
#             " ("            + str(self.ratio_of_untracked()) + ") "
#         s += "Class: "    + str(number_of_untracked_class_level) + \
#             " ("            + str(self.ratio_of_untracked_class_level()) + ") "
#         s += "Method: "   + str(number_of_untracked_method_level) + \
#             " ("            + str(self.ratio_of_untracked_method_level()) + ") "
#         s += "Matching: "+ str(number_of_matching) + \
#             " ("            + str(self.ratio_of_matching()) + ") "
#         s += "Non-matching: "  + str(number_of_non_matching) + \
#             " ("            + str(self.ratio_of_non_matching()) + ")"
#         s += str(self.count_relations())
        s = ""
        s += str(number_of_versions) + " "
        s += str(number_of_relations) + " "
        s += str(number_of_tracked) + " "
        s += str(self.ratio_of_tracked()) + " "
        s += str(number_of_tracked_class_level) + " "
        s += str(self.ratio_of_tracked_class_level()) + " "
        s += str(number_of_tracked_method_level) + " "
        s += str(self.ratio_of_tracked_method_level()) + " "
        s += str(number_of_untracked) + " "
        s += str(self.ratio_of_untracked()) + " "
        s += str(number_of_untracked_class_level) + " "
        s += str(self.ratio_of_untracked_class_level()) + " "
        s += str(number_of_untracked_method_level) + " "
        s += str(self.ratio_of_untracked_method_level()) + " "
        s += str(number_of_matching) + " "
        s += str(self.ratio_of_matching()) + " "
        s += str(number_of_non_matching) + " "
        s += str(self.ratio_of_non_matching()) + "\n"
        s += str(self.count_relations())

        return s
        
class Version:
    
    def __init__(self, commit, date):
        self.commit = commit
        self.date = date
        self.relations = []
        
    def trackeds(self):
        return ModelUtil().trackeds(self.relations)
    
    def untrackeds(self):
        return ModelUtil().untrackeds(self.relations)
    
    def matchings(self):
        return ModelUtil().matchings(self.relations)
    
    def non_matchings(self):
        return ModelUtil().non_matchings(self.relations)
    
    def __str__(self):
        #s = "Version: " + self.commit
        s = "Version " + str(self.date) + ", "
        s += "relations " + str(len(self.relations)) + ", "
        s += "refs " + str(len(self.untrackeds())) + ", "
        s += "matchings " + str(len(self.matchings())) + ", "
        s += str(self.count_untrackeds())
        s += "\n"
        return s

class Entity:
    
    def __init__(self, name):
        self.name = name
        self.next = []
        self.previous = []
        
    def add_next(self, entity):
        self.next.append(entity)
        
    def add_previous(self, node):
        self.previous.append(node)
        
    def __str__(self):
        return self.name

class SimpleRelation:

    def __init__(self, name):
        self.name = name
        
    def method_level(self):
        return self.name.endswith("Method")
    
    def class_level(self):
        return not self.method_level()

    def is_change(self):
        return self.name.startswith("Same")
    
    def is_refactoring(self):
        return not self.not_refactoring()
    
    def not_refactoring(self):
        return self.is_change()
    
    def tracked(self):
        return self.not_refactoring()
    
    def untracked(self):
        return self.is_refactoring()
    
    def is_matching(self):
        return self.is_refactoring() and not self.non_matching()
    
    def non_matching(self):
        #Extract Method, Extract Supertype, Inline Method
        return self.is_refactoring() and (self.name.startswith("Extract") or self.name.startswith("Inline"))

class Relation(SimpleRelation):
    
    def __init__(self, name, commit, entity1, entity2):
        self.name = name
        self.entity1 = entity1
        self.entity2 = entity2
        self.commit = commit
        
        self.alternative_name1 = self.entity1.name
        self.alternative_name2 = self.entity2.name
        
        self.entity1.add_next(self.entity2)
        self.entity2.add_previous(self.entity1)
        
        self.ok = True
    
    def with_change(self):
        return self.ok and self.is_change()
    
    def with_matching(self):
        return self.with_change() or self.is_matching()
    
    def with_nonmatching(self):
        return self.with_matching() or self.non_matching()
    
    def is_root(self):
        return self.ok #and self.is_addition()
    
    def not_ok(self):
        self.ok = False
        
    def full_name(self):
        return self.name + " "  + self.commit + " " + self.entity1.name + " " + self.entity2.name
        
    def __str__(self):
        return self.name

class CheminElement:
    
    separator = ModelHistory.path_element_separator
    
    def __init__(self, full_name):
        self.full_name = full_name
        self.name = full_name.split(self.separator)[0].rstrip()
        self.count = full_name.split(self.separator)[1].rstrip()
        self.relation_name = full_name.split(self.separator)[2].rstrip()
    
    def is_tracked(self):
        return self.relation_name == "SameType" or self.relation_name == "SameMethod"
    
    def is_untracked(self):
        return not self.is_tracked()
    
    def name_and_relation(self):
        return self.name + " " + self.relation_name + "\n"
    
    def __str__(self):
        s = self.full_name + "\n"
        #s += "Name: " + self.name + " "
        #s += "Count: " + self.count + " "
        #s += "Relation name: " + self.relation_name + " "
        return s
        

class Chemin:
    
    def __init__(self, elements):
        self.chemin_elements = []
        self.update_elements(elements)
    
    def update_elements(self, elements):
        for element in elements:
            chemin_element = CheminElement(element)
            self.chemin_elements.append(chemin_element)
    
    def has_untracked_change(self):
        for element in self.chemin_elements:
            if element.is_untracked():
                return True
        return False
    
    def element_names(self):
        return map(lambda elem: elem.name_and_relation() , self.chemin_elements)
    
    def unique_element_names(self):
        return self.remove_duplicates(self.element_names())
    
    def size(self):
        return len(self.chemin_elements)-1
    
    def size_unique_elements(self):
        return len(self.unique_element_names())
    
    def print_unique_element_names(self):
        s = ""
        for element in self.unique_element_names():
            s += element + "\n"
        return s
    
    def remove_duplicates(self, elements):
        #TODO, a kind of ordered set
        ordered = []
        for each in elements:
            if each not in ordered:
                ordered.append(each)
        return ordered
    
    def __str__(self):
        s = ""
        for element in self.chemin_elements:
            s += element.__str__()
        return s + "\n"

class Path:
    
    def __init__(self, path_tuple):
        self.root = path_tuple[0]
        self.chemin = Chemin(path_tuple[1])
    
    def has_tracked_change(self):
        return self.chemin.has_tracked_change()
    
    def has_untracked_change(self):
        return self.chemin.has_untracked_change()
    
    def relations(self):
        return self.chemin.relations()
        
    def path_element_names(self):
        return self.chemin.element_names()
    
    def path_unique_element_names(self):
        return self.chemin.unique_element_names()
    
    def size(self):
        return self.chemin.size()
    
    def size_unique_elements(self):
        return self.chemin.size_unique_elements()
    
    def print_path_unique_element_names(self):
        return str(self.size_unique_elements()) + "\n" + str(self.chemin.print_unique_element_names())
    
    def __str__(self):
        return "Root: " + self.root + " " + str(self.size()) + " " + str(self.has_untracked_change()) + "\n" + str(self.chemin)
    
class GraphAnalysis:
    
    def __init__(self, model):
        self.model = model
        self.graph = nx.DiGraph()
        
        self.add_edges()
        self.nodes = nx.nodes(self.graph)
        
        self.roots = []
        self.update_roots()
        
        self.paths = []
        self.update_longest_paths()
        
    def print_paths(self):
        s = "Paths: " + str(len(self.paths)) + "\n"
        for path in self.paths:
            s += path.__str__()
        return s
    
    def print_unique_paths(self):
        s = "Paths: " + str(len(self.paths)) + "\n"
        for path in self.paths_sorted_by_unique_elements():
            s += path.print_path_unique_element_names()
        return s
    
    def paths_sorted_by_unique_elements(self):
        return sorted(self.paths, key=(lambda path: path.size_unique_elements()), reverse=True)
        
    def add_edges(self):
        for edge in self.model.relations:
            self.graph.add_edge(edge.alternative_name1, edge.alternative_name2)
    
    def paths_with_tracked_changes(self):
        return filter(lambda path: path.has_tracked_change(), self.paths)
    
    def paths_with_untracked_changes(self):
        return filter(lambda path: path.has_untracked_change(), self.paths)
    
    def path_sizes(self):
        #Remove the paths with size == 1 because they have only one addition
        return map(lambda path: path.size(), self.paths)
    
    def unique_path_sizes(self):
        #Remove the paths with size == 1 because they have only one addition
        return map(lambda path: path.size_unique_elements(), self.paths_sorted_by_unique_elements())
    
    def node_has_zero_degree(self, node):
        return self.graph.in_degree(node) == 0
    
    def update_roots(self):
        self.roots = filter(lambda node: self.node_has_zero_degree(node), self.nodes)
    
    def update_longest_paths(self):
        path_tuples = self.compute_longest_path_for_roots()
        self.create_paths(path_tuples)
    
    def create_paths(self, path_tuples):
        for path_tuple in path_tuples:
            self.paths.append(Path(path_tuple))
    
    def compute_longest_path_for_roots(self):
        result = {}
        for root in self.roots:
            result[root] = self.longest_path_for(root)
        return sorted(result.items(), key=(lambda x: len(x[1])), reverse=True)
    
    def longest_path_for(self, node):
        paths = nx.shortest_path(self.graph, source=node)
        return max(paths.values(), key=len)

def print_models(model_path):
    
#     print model_path
    
#     model = ModelHistory(model_path, True)
#     g = GraphAnalysis(model)
#     print g.roots
#     print g.print_paths()
#     print g.path_sizes()
#     print model
    
#     model = ModelHistory(model_path, True, True)
#     g = GraphAnalysis(model)
#     print g.roots
#     print g.print_paths()
#     print g.path_sizes()
#     print model
    
    model = ModelHistory(model_path, True, True, True)
    g = GraphAnalysis(model)
#     print g.roots
#     print g.print_paths()
#     print g.path_sizes()
#     print g.print_unique_paths()
#     print g.unique_path_sizes()
#     print model
    print len(g.paths_with_tracked_changes())
    print len(g.paths_with_untracked_changes())
    
print_models("../history_models/model_RxJava")
# print_models("../history_models/model_elasticsearch")
# print_models("../history_models/model_retrofit")
# print_models("../history_models/model_okhttp")
# print_models("../history_models/model_guava")
# print_models("../history_models/model_MPAndroidChart")
# print_models("../history_models/model_Glide")
# print_models("../history_models/model_Android-Universal-Image-Loader")
# print_models("../history_models/model_kotlin")
# print_models("../history_models/model_spring-framework")
# print_models("../history_models/model_fresco")
# print_models("../history_models/model_clojure")
# print_models("../history_models/model_guice")
# print_models("../history_models/model_storm")
# print_models("../history_models/model_che")
#print_models("../history_models/all")

# graph = nx.DiGraph()
# graph.add_edge("A","B")
# graph.add_edge("B","C")
# graph.add_edge("C","D")
# print nx.shortest_path_length(graph, 'A')
# print nx.shortest_path(graph)
# print graph.in_degree('D')