#!/usr/bin/python
import pprint
import copy

#############################

#TODO unused
#sentence is a list of strings
def parse(sentence):

    #start column 1
    column = []

    #add root node
    column.append(Rule(0, "Root", ["S"]))


#############################


class Rule:
    #where this rule started to apply
    #start = 0
    #one string, left hand side of this rule
    #LHS
    #list of strings, expansion of the left hand side
    #RHS
    #index of our position in the rule
    #index


    def __init__(self, start, LHS, RHS, index):
        self.start = start
        self.LHS = LHS
        self.RHS = RHS
        self.index = index

    def __str__(self):
        return "<"+str(self.start)+" "+self.LHS+":"+str(self.RHS)+" "+ str(self.index)+">"

    def __repr__(self):
        return "<"+str(self.start)+" "+self.LHS+":"+str(self.RHS)+" "+ str(self.index)+">"


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



#############################


#table for parsing a sentence
parse_table = []

#list of rules
rule_table = [
    Rule(0, "ROOT", ["S"], 0),
    Rule(0, "S", ["NP", "VP"], 0),
    Rule(0, "NP", ["Jane"], 0),
    Rule(0, "VP", ["eats"], 0)
    ]



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
def predict_entire_column(column_number):
    global parse_table
    column = parse_table[column_number]

    unchecked_rules = copy.deepcopy(column)
    pprint.pprint("unchecked: " + str(unchecked_rules))
    pprint.pprint("column: " + str(column))

    while(len(unchecked_rules) != 0):

        if (not unchecked_rules[0].is_complete()):
            new_rules = predict(unchecked_rules[0], column_number)

            print "### new_rules: " + str(new_rules)
            unchecked_rules = unchecked_rules + new_rules

        unchecked_rules = unchecked_rules[1:]
        pprint.pprint("unchecked: " + str(unchecked_rules))


#return true if we add rules
#return false if we add no rules
def predict(rule, column_number):
    global parse_table

    added_rules = []
    next_symbol = rule.get_next_scan_symbol()
    column = parse_table[column_number]

    if (not column_already_contains_LHS(next_symbol, column)):
        rules = get_all_rules_starting_with(next_symbol, column_number)

        print "### rules " + str(rules)

        for rule in rules:
            if (not rule in column):
                column.append(rule)
                added_rules.append(rule)

    return added_rules


def column_already_contains_LHS(LHS, column):
    return LHS in map(lambda x: x.get_LHS(), column)


#symbol rules must start with
#column_number - column this rule will start in
def get_all_rules_starting_with(symbol, column_number):
    global rule_table
    rules = filter(lambda x: x.matches_start_symbol(symbol), rule_table)
    for rule in rules:
        rule.set_start(column_number)
    return rules



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

    #add root symbol
    root_rule = Rule(0, "ROOT", ["S"], 0)
    add_rule_to_parse_table(root_rule, 0)

    column_number = 0

    #for each column
    while column_number < len(parse_table):
    #will if be a problem if we add cols as we do this loop?

        print "start loop" + str(column_number)
        print_parse_table()

        #attach any completed rules backwards
        attach_all_completed_rules(column_number)
            #and check if those rules complete, attach etc.

        print "attach:"
        print_parse_table()

        #fully predict column
        predict_entire_column(column_number)

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
    return parse_table[-1][-1].is_complete() #TODO and it's root


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
print earley(["Jane","eats"])
