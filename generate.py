#!/usr/bin/python
import sys
import re


#rules are of the format
#LHS : [RHS1 RHS2 ...]
rules = {}



def parse_grammar_file(filename):
    global rules
    f = open(filename, 'r')
    for line in f:
        if (line[0] != "#" and (not re.match(line.strip(), '\s'))):
            #print "###" + line
            #skip empty lines
            #skip comments
            line = line.split("#")[0] #remove comments

            split = line.strip().split()
            weight = split[0]
            LHS = split[1]
            RHS = split[2:]

            rules[LHS] = RHS


#for all non-comment non-empty lines parse as
#weight LHS <tab> RHS
    #rhs may have multiple elements




def create_sentences(n):
    print "nope"



############
##main

grammar_filename = sys.argv[1]
number_of_words = sys.argv[2]

parse_grammar_file(grammar_filename)
create_sentences(number_of_words)


print rules
