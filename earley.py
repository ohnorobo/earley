#!/usr/bin/python
import pprint
import copy
import sys
import re



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

    #get the rhs of this rule
    #listof string
    def get_RHS(self):
        return self.RHS

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
class EarleyParser():

    def __init__(self, rules):
        #table for parsing a sentence
        self.parse_table = []

        #list of rules
        self.rule_table = self.sort_rules_by_LHS(rules)

        #left corner
        #TODO- generate this from rules
        #map of symbols -> list of potential terminals that they can start with
        # NP -> ["the", "a", "Papa"]
        # PP -> ["in", "with"]
        self.left_corner = self.generate_left_corner_table()

        #pprint.pprint(self.rule_table)
        #pprint.pprint(self.left_corner)


    #takes a list of rules
    #and returns a dict of {LHS -> list of rules}
    def sort_rules_by_LHS(self, rules_list):
        rules = {}

        for rule in rules_list:
            LHS = rule.get_LHS()
            if LHS in rules.keys():
                rules[LHS].append(rule)
            else:
                rules[LHS] = [rule]

        return rules


    #############################
    # Generate the left-corner table for optimization

    # this will fail if 2 rules have cyclic left-corner dependancies
    # ex:
    # XP -> YP Z
    # YP -> XP Z
    # haha this has been fixed now

    # returns left corner table
    # { LHS -> [all possible starting words] }
    def generate_left_corner_table(self):
        initial_left_corner = {}
        final_left_corner = {}
        non_terminals = self.rule_table.keys()

        for non_terminal in non_terminals:
            my_nonterminals, my_terminals = self.get_immediate_left_corner(
                non_terminal, non_terminals)

            initial_left_corner[non_terminal] = [my_nonterminals, my_terminals]
            final_left_corner[non_terminal] = [my_nonterminals, my_terminals]

        for key in final_left_corner.keys():
            self.resolve_non_terminals(key, final_left_corner, initial_left_corner)

        left_corner = {}
        for key in final_left_corner.keys():
            left_corner[key] = set(final_left_corner[key][1])
            #get only terminals
            #use sets to remove dups and make contains faster

        #pprint.pprint(left_corner)

        return left_corner

    # given a LHS resolved all the nonterminals for that LHS un final_left using initial_left
    # this will deal correctly with cyclic dependancies between rules
    # although it may resolve the same path many times
    # and it uses more memory than needed since many terminal lists are repeated
    # instead of being resolved dynamically
    def resolve_non_terminals(self, LHS, final_left_corner, initial_left_corner):
        my_nonterminals = final_left_corner[LHS][0]
        my_terminals = final_left_corner[LHS][1]
        my_resolved_nonterminals = [LHS]

        while my_nonterminals:
            non_terminal = my_nonterminals[0]

            new_nonterminals = initial_left_corner[non_terminal][0]
            new_terminals = initial_left_corner[non_terminal][1]

            my_nonterminals.remove(non_terminal)
            my_resolved_nonterminals.append(non_terminal)
            for n in new_nonterminals: my_nonterminals.append(n)
            for n in new_terminals: my_terminals.append(n)

            #remove previously resolved nonterminals
            for nt in my_resolved_nonterminals:
                if nt in my_nonterminals:
                    my_nonterminals.remove(nt)

    # returns a list of nonterminals in the left corner of this LHS's rules
    # and a list of terminals
    def get_immediate_left_corner(self, LHS, non_terminals):
        rules_with_LHS = self.rule_table[LHS]
        my_terminals = []
        my_nonterminals = []
        for rule in rules_with_LHS:
            left_corner = rule.get_RHS()[0]
            if left_corner in non_terminals:
                my_nonterminals.append(left_corner)
            else:
                my_terminals.append(left_corner)
        return my_nonterminals, my_terminals



    #############################


    #scan entire table
    def scan(self, word, column_number):
        #scan over all next-symbols in column
        #if any match word increment the rule and place it in the next column
        #must scan over all rules evan after a match because lexical ambiguity
        for rule in self.parse_table[column_number]:
            if (not rule.is_complete() and rule.can_scan(word)):
                new_rule = rule.get_moved_rule()
                self.add_rule_to_parse_table(new_rule, column_number+1)



    #############################

    # check every rule in a column
    # (including rules added while running this method)
    # and add their expansions to the column
    def predict_entire_column(self, column_number, sentence):
        column = self.parse_table[column_number]

        unchecked_rules = copy.deepcopy(column)
        #pprint.pprint("unchecked: " + str(unchecked_rules))
        #pprint.pprint("column: " + str(column))

        while(len(unchecked_rules) != 0):

            if (not unchecked_rules[0].is_complete()):
                new_rules = self.predict(unchecked_rules[0], column_number, sentence)

                #print "### new_rules: " + str(new_rules)
                unchecked_rules = unchecked_rules + new_rules

            unchecked_rules = unchecked_rules[1:]
            #pprint.pprint("unchecked: " + str(unchecked_rules))


    #return true if we add rules
    #return false if we add no rules
    def predict(self, rule, column_number, sentence):

        added_rules = []
        next_symbol = rule.get_next_scan_symbol()
        column = self.parse_table[column_number]

        #print "trying to add rules for " + next_symbol
        if (not self.column_already_contains_LHS(next_symbol, column)):
            #print "success"
            rules = self.get_all_rules_starting_with(next_symbol)

            #print "### rules " + str(rules)

            for rule in rules:
                if (self.matches_left_corner(column_number, rule, sentence)
                    and not rule in column):

                    rule.set_start(column_number)
                    column.append(rule)
                    added_rules.append(rule)

        return added_rules


    #only returns true if a column already has a rule with this start symbol,
    #and its index is 0 (ie it was started in this column)
    def column_already_contains_LHS(self, LHS, column):
        new_rules = filter(lambda x: x.is_not_started(), column)
        #print "filter" + str(new_rules)
        return LHS in map(lambda x: x.get_LHS(), new_rules)


    #symbol rules must start with
    #column_number is the column this rule will start in
    def get_all_rules_starting_with(self, symbol):
        #rules = filter(lambda x: x.matches_start_symbol(symbol), self.rule_table)
        if symbol in self.rule_table.keys():
            rules = self.rule_table[symbol]
            #for rule in rules:
            #    rule.set_start(column_number)
            return rules
        else:
            return []


    #true if the left-corner set for this rule matches the next word in the sentence
    def matches_left_corner(self, column_num, rule, sentence):
        if (column_num > len(sentence)-1):
            return False #no further prediction if sentence is over
        else:
            lookahead_word = sentence[column_num]
            symbol = rule.get_next_scan_symbol()

            #print "lookahead" + lookahead_word
            #print rule.get_LHS()
            #print self.left_corner[symbol]

            if symbol in self.left_corner.keys():
                return lookahead_word in self.left_corner[symbol]
            else:
                return lookahead_word == symbol


    #############################


    def attach(self, completed_rule, column_number):

        completed_symbol = completed_rule.get_LHS()
        started = completed_rule.get_start_column_number()

        #for the column this rule started in
        column = self.parse_table[started]

        for rule in column:
            if (not rule.is_complete() and rule.can_scan(completed_symbol)):
                #add the moved rule to the column completed_rule ended in
                self.add_rule_to_parse_table(rule.get_moved_rule(), column_number)

    def attach_all_completed_rules(self, column_number):
        for rule in self.parse_table[column_number]:
            if rule.is_complete():
                self.attach(rule, column_number)


    #############################


    #sentence is a list of words/punctuation
    def parse(self, sentence):
        self.parse_table = []

        #add root symbol
        root_rule = Rule(0, "START", ["ROOT"], 0)
        self.add_rule_to_parse_table(root_rule, 0)

        column_number = 0

        #for each column
        while column_number < len(self.parse_table):
        #will if be a problem if we add cols as we do this loop?

            #print "##"
            #print "start loop" + str(column_number)

            #attach any completed rules backwards
            self.attach_all_completed_rules(column_number)
                #and check if those rules complete, attach etc.

            #print "attach:"
            #self.print_parse_table()

            #fully predict column
            self.predict_entire_column(column_number, sentence)

            #print "predict:"
            #self.print_parse_table()

            #scan column and start filling out next one
            if (column_number < len(sentence)): #if there's more sentence to scan
                self.scan(sentence[column_number], column_number)

                #print "scan"
                #self.print_parse_table()

            column_number += 1 #increment

        #if Root is complete end
        #print "END"
        #print str(sentence)
        #self.print_parse_table()

        if (column_number == 1 + len(sentence)):
            return self.parse_table_complete()
        else:
            return False


    #was this parse table finished successfully
    #ie "0 Root -> S." is in the last column
    def parse_table_complete(self):
        return Rule(0, "START", ["ROOT"], 1) in self.parse_table[-1]


    def print_parse_table(self):

        print "####"
        pprint.pprint(self.parse_table)
        print ""



    def add_rule_to_parse_table(self, rule, column_number):
        if len(self.parse_table) > column_number:
            self.parse_table[column_number].append(rule)
        elif len(self.parse_table) == column_number:
            self.parse_table.append([rule])
        else:
            print "### trying to add to a column out of range " + str(column_number)




#############################

#parse rules, parse sentence,
def main():

    grammar_filename = sys.argv[1] #first arg is the filename
    sentence_filename = sys.argv[2] #second arg is the sentence filename
    rules = []
    pattern = re.compile('^\s*$') #line with only whitespace

    f = open(grammar_filename, 'r')
    for line in f:
        if (line[0] != "#" and (not pattern.match(line.strip()))):
            line = line.split("#")[0] #remove comments

            split = line.strip().split()
            weight = float(split[0])
            LHS = split[1]
            RHS = split[2:]
            rules.append(Rule(0, LHS, RHS, 0))

    earley = EarleyParser(rules)

    f2 = open(sentence_filename, 'r')
    for sentence in f2:
        print str(earley.parse(sentence.split())).lower() # print 'true' instead of 'True'

if __name__ == "__main__":
    main()
