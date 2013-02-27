#!/usr/bin/python

import sys, string, re, pprint, random


#rules are of the format
#LHS : [(RHS1, w1),  (RHS2, w2) ...]
rules = {}
total_weights = {}


def parse_grammar_file(filename):
    global rules
    global total_weights
    f = open(filename, 'r')
    for line in f:
        if (line[0] != "#" and (not re.match(line.strip(), '\s'))):
            #skip empty lines
            #skip comments
            line = line.split("#")[0] #remove comments

            #print "###" + line

            split = line.strip().split()
            weight = int(split[0])
            LHS = split[1]
            RHS = split[2:]

            #rules[LHS] = RHS
            if LHS in rules:
                rules[LHS].append((RHS, weight))
                total_weights[LHS] += weight
            else:
                rules[LHS] = [(RHS, weight)]
                total_weights[LHS] = weight


#for all non-comment non-empty lines parse as
#weight LHS <tab> RHS
    #rhs may have multiple elements


#creates a new sentence using rewrites
def create_sentence():
    return flatten(rewrite_node("ROOT"))


#takes a list of terminals/nonterminals
#and rewrites them as far down as possible
def rewrite_node(node):
    #print "## " + "rewriting sentence " + str(node)
    #for i in range(len(sentence)):

    #node = sentence[i]
    if node in rules.keys(): #nonterminal
        #print "## node " + node
        rewrite = random.choice(rules[node])[0]
        #print "## rewriting " + node + " to " + str(rewrite)

        filtered =  map(rewrite_node, rewrite)
        #print "### filtered:"
        #pprint.pprint( filtered)
        return filtered
    else: #terminal
        #print "## terminal " + node
        return node



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
pprint.pprint( total_weights )

for i in range(int(number_of_words)):
    sentence = create_sentence()
    #print "\n# sentence"
    pprint.pprint( string.join(sentence, " ") )
