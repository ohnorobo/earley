#!/usr/bin/python

import sys
import re
import pprint
import random


#rules are of the format
#LHS : [RHS1 RHS2 ...]
rules = {}



def parse_grammar_file(filename):
    global rules
    f = open(filename, 'r')
    for line in f:
        if (line[0] != "#" and (not re.match(line.strip(), '\s'))):
            #skip empty lines
            #skip comments
            line = line.split("#")[0] #remove comments

            #print "###" + line

            split = line.strip().split()
            weight = split[0]
            LHS = split[1]
            RHS = split[2:]

            #rules[LHS] = RHS
            if LHS in rules:
                rules[LHS].append(RHS)
            else:
                rules[LHS] = [RHS]


#for all non-comment non-empty lines parse as
#weight LHS <tab> RHS
    #rhs may have multiple elements


#creates a new sentence using rewrites
def create_sentences(n):
    return flatten(rewrite_node("ROOT"))


#takes a list of terminals/nonterminals
#and rewrites them as far down as possible
def rewrite_node(node):
    print "## " + "rewriting sentence " + str(node)
    #for i in range(len(sentence)):

    #node = sentence[i]
    if node in rules.keys(): #nonterminal
        print "## node " + node
        rewrite = random.choice(rules[node])
        print "## rewriting " + node + " to " + str(rewrite)

        filtered =  map(rewrite_node, rewrite)
        print "### filtered:"
        pprint.pprint( filtered)
        return filtered
    else: #terminal
        print "## terminal " + node
        return node

#make sure "NP" isn't being parsed into chars

#def contains_nonterminals()

#http://caolanmcmahon.com/posts/flatten_for_python/
#turn an arbitrarily nested list into a linear one
def flatten(l):
    return reduce(lambda x,y: x+[y] if type(y) != list else x+flatten(y), l,[])


############
##main

grammar_filename = sys.argv[1]
number_of_words = sys.argv[2]

parse_grammar_file(grammar_filename)

print "# rules"
pprint.pprint( rules )

sentence = create_sentences(number_of_words)
print "\n# sentence"
pprint.pprint( sentence )
