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
            weight = float(split[0])
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
    sentence = rewrite_node("ROOT")
    pprint.pprint(sentence)
    return flatten(sentence)


#takes a list of terminals/nonterminals
#and rewrites them as far down as possible
def rewrite_node(node):
    #print "## " + "rewriting sentence " + str(node)
    #for i in range(len(sentence)):

    #node = sentence[i]
    if node in rules.keys(): #nonterminal
        #print "## node " + node
        #rewrite = random.choice(rules[node])[0]
        rewrite = choose_probabilistic(rules[node])
        print "## rewriting " + node + " to " + str(rewrite)

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

#list if a list of (item, weight)
def choose_probabilistic(list):
    weights = [x[1] for x in list]
    i = get_random_weighted_index(weights)
    return list[i][0]

#http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/
#returns an index of the weighted list with prob of each choice = weight/total
def get_random_weighted_index(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

############
##main

grammar_filename = sys.argv[1]
number_of_words = sys.argv[2]

parse_grammar_file(grammar_filename)

#print "# rules"
#pprint.pprint( rules )
#pprint.pprint( total_weights )

for i in range(int(number_of_words)):
    sentence = create_sentence()
    #print "\n# sentence"
    pprint.pprint( string.join(sentence, " ") )
