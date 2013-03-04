#!/usr/bin/python
import pprint
import copy


#############################


class Rule:

    # a rule of the form
    # N LHS -> RHS M
    # ex:  0, S -> NP VP, 1

    def __init__(self, start, LHS, RHS, index):
        #where this rule started to apply
        self.start = start
        #one string, left hand side of this rule
        self.LHS = LHS
        #list of strings, expansion of the left hand side
        self.RHS = RHS
        #index of our position in the rule
        self.index = index

    def __str__(self):
        return "<"+str(self.start)+" "+self.LHS+":"+str(self.RHS)+" "+ str(self.index)+">"

    def __repr__(self):
        return "<"+str(self.start)+" "+self.LHS+":"+str(self.RHS)+" "+ str(self.index)+">"

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


    #get the column number this rule started in
    #int
    def get_start_column_number(self):
        return self.start

    #set the start number
    def set_start(self, n):
        self.start = n

    #get a new rule like this one but iterated by one
    #Rule
    def get_moved_rule(self):
        return Rule(self.start, self.LHS, self.RHS, self.index+1)

    #get a new rule like this one with a given start
    #Rule
    def get_rule_copy(self, start):
        return Rule(self.start, self.LHS, self.RHS, 0)

    #get the lhs of this rule
    #string
    def get_LHS(self):
        return self.LHS

    #does the given symbol match the symbol we're looking for?
    #boolean
    def can_scan(self, symbol):
        #if not self.is_complete():
        #    return false
        #else:
        return symbol == self.RHS[self.index]

    #get the symbol we want to scan next
    #string
    def get_next_scan_symbol(self):
        return self.RHS[self.index]

    #does the given symbol match the start symbol of this rule
    #boolean
    def matches_start_symbol(self, symbol):
        return symbol == self.LHS

    #is this rule complete/
    #(all symbols in the rule have been matched)
    #boolean
    def is_complete(self):
        return self.index == len(self.RHS)

    #returns true of this rule hasn't been started
    #boolean
    def is_not_started(self):
        return self.index == 0



#############################


#table for parsing a sentence
parse_table = []

#list of rules
'''
rule_table = [
    Rule(0, "ROOT", ["S"], 0),
    Rule(0, "S", ["NP", "V"], 0),
    Rule(0, "VP", ["V", "NP"], 0),
    Rule(0, "NP", ["ADJ", "NP"],0),

    Rule(0, "NP", ["Jane"], 0),
    Rule(0, "ADJ", ["silly"], 0),
    Rule(0, "V", ["eats"], 0),
    Rule(0, "V", ["cries"], 0)
    ]
'''

rule_table = [
    Rule(0, "ROOT", ["S"], 0),
    Rule(0, "S", ["NP", "VP"], 0),
    Rule(0, "NP", ["Det", "N"], 0),
    Rule(0, "NP", ["NP", "PP"], 0),
    Rule(0, "VP", ["V", "NP"], 0),
    Rule(0, "VP", ["VP", "PP"], 0),
    Rule(0, "PP", ["P", "NP"], 0),

    Rule(0, "NP", ["Papa"], 0),
    Rule(0, "N", ["caviar"], 0),
    Rule(0, "N", ["spoon"], 0),
    Rule(0, "V", ["ate"], 0),
    Rule(0, "P", ["with"], 0),
    Rule(0, "Det", ["the"], 0),
    Rule(0, "Det", ["a"], 0)
    ]




#left corner
#TODO- generate this from rules
#map of symbols -> list of potential terminals that they can start with
# NP -> ["the", "a", "Papa"]
# PP -> ["in", "with"]
left_corner = {
    "ROOT" : ["Papa", "the", "a", "caviar", "spoon"],
    "S" :  ["Papa", "the", "a", "caviar", "spoon"],
    "NP" : ["Papa", "the", "a", "caviar", "spoon"],
    "VP" : ["ate"],
    "PP" : ["with"],
    "N" : ["Papa", "caviar", "spoon"],
    "V" : ["ate"],
    "P" : ["with"],
    "Det" : ["the", "a"]
    }


#############################


#scan entire table
def scan(word, column_number):
    global parse_table
    #scan over all next-symbols in column
    #if any match word increment the rule and place it in the next column
    #must scan over all rules evan after a match because lexical ambiguity
    for rule in parse_table[column_number]:
        if (not rule.is_complete() and rule.can_scan(word)):
            new_rule = rule.get_moved_rule()
            ##parse_table[column_number+1].append(new_rule)
            add_rule_to_parse_table(new_rule, column_number+1)



#############################

# check every rule in a column
# (including rules added while running this method)
# and add their expansions to the column
def predict_entire_column(column_number, sentence):
    global parse_table
    column = parse_table[column_number]

    unchecked_rules = copy.deepcopy(column)
    #pprint.pprint("unchecked: " + str(unchecked_rules))
    #pprint.pprint("column: " + str(column))

    while(len(unchecked_rules) != 0):

        if (not unchecked_rules[0].is_complete()):
            new_rules = predict(unchecked_rules[0], column_number, sentence)

            #print "### new_rules: " + str(new_rules)
            unchecked_rules = unchecked_rules + new_rules

        unchecked_rules = unchecked_rules[1:]
        #pprint.pprint("unchecked: " + str(unchecked_rules))


#return true if we add rules
#return false if we add no rules
def predict(rule, column_number, sentence):
    global parse_table

    added_rules = []
    next_symbol = rule.get_next_scan_symbol()
    column = parse_table[column_number]

    #print "trying to add rules for " + next_symbol
    if (not column_already_contains_LHS(next_symbol, column)):
        #print "success"
        rules = get_all_rules_starting_with(next_symbol, column_number)

        #print "### rules " + str(rules)

        for rule in rules:
            if (not rule in column
                and matches_left_corner(column_number, rule, sentence)):

                column.append(rule)
                added_rules.append(rule)

    return added_rules


#only returns true if a column already has a rule with this start symbol,
#and its index is 0 (ie it was started in this column)
def column_already_contains_LHS(LHS, column):
    new_rules = filter(lambda x: x.is_not_started(), column)
    #print "filter" + str(new_rules)
    return LHS in map(lambda x: x.get_LHS(), new_rules)


#symbol rules must start with
#column_number is the column this rule will start in
def get_all_rules_starting_with(symbol, column_number):
    global rule_table
    rules = filter(lambda x: x.matches_start_symbol(symbol), rule_table)
    for rule in rules:
        rule.set_start(column_number)
    return rules


#true if the left-corner set for this rule matches the next word in the sentence
def matches_left_corner(column_num, rule, sentence):
    if (column_num > len(sentence)-1):
        return False #no further prediction is sentence is over
    else:
        lookahead_word = sentence[column_num]
        symbol = rule.get_LHS()
        return lookahead_word in left_corner[symbol]


#############################


def attach(completed_rule, column_number):
    global parse_table

    completed_symbol = completed_rule.get_LHS()
    started = completed_rule.get_start_column_number()

    #for the column this rule started in
    column = parse_table[started]

    for rule in column:
        if (not rule.is_complete() and rule.can_scan(completed_symbol)):
            #add the moved rule to the column completed_rule ended in
            add_rule_to_parse_table(rule.get_moved_rule(), column_number)

def attach_all_completed_rules(column_number):
    global parse_table
    for rule in parse_table[column_number]:
        if rule.is_complete():
            attach(rule, column_number)


#############################


def earley(sentence):
    global parse_table
    parse_table = []

    #add root symbol
    root_rule = Rule(0, "ROOT", ["S"], 0)
    add_rule_to_parse_table(root_rule, 0)

    column_number = 0

    #for each column
    while column_number < len(parse_table):
    #will if be a problem if we add cols as we do this loop?

        print "##"
        print "start loop" + str(column_number)

        #attach any completed rules backwards
        attach_all_completed_rules(column_number)
            #and check if those rules complete, attach etc.

        print "attach:"
        print_parse_table()

        #fully predict column
        predict_entire_column(column_number, sentence)

        print "predict:"
        print_parse_table()

        #scan column and start filling out next one
        if (column_number < len(sentence)): #if there's more sentence to scan
            scan(sentence[column_number], column_number)

            print "scan"
            print_parse_table()

        column_number += 1 #increment

    #if Root is complete end
    print "END"
    print str(sentence)
    return parse_table_complete(parse_table)


#was this parse table finished successfully
#ie "0 Root -> S." is in the last column
def parse_table_complete(parse_table):
    return Rule(0, "ROOT", ["S"], 1) in parse_table[-1]


def print_parse_table():

    print "####"
    pprint.pprint(parse_table)
    print ""



def add_rule_to_parse_table(rule, column_number):
    global parse_table
    if len(parse_table) > column_number:
        parse_table[column_number].append(rule)
    elif len(parse_table) == column_number:
        parse_table.append([rule])
    else:
        print "### trying to add to a column out of range " + str(column_number)


#test
'''
print earley(["Jane","eats"])
print "#######\n"
print earley(["Jane","eats","Jane"])
print "#######\n"
print earley(["Jane"])
print "#######\n"
print earley(["silly", "Jane","eats","Jane"])
print "#######\n"
print earley(["Jane", "silly","eats","Jane"])
print "#######\n"
'''

print earley(["Papa", "ate", "the", "caviar", "with", "the", "spoon"])
print "#######\n"





