#!/usr/bin/env python2


import sys
import re


# if filtering is enabled then print everything which doesn't match
filtering = True 


if len(sys.argv) > 3:
    print >> sys.stderr, "Too many arguments"
    exit(1)


error_string = ''
for arg in sys.argv:
    if arg == '-match':
        filtering = False
    else:
        error_string = arg

if not error_string:
    print >> sys.stderr, "No search string provided"
    exit(1)


# make the search string ignore whitespace
# This could cause very strange behaviour
error_string = re.sub(' ', '\\s*', error_string)
print >>sys.stderr, 'Warning: whitespaces have been replaced in the search string'

if filtering:
    print >>sys.stderr, 'Filtering occurences of \'' + error_string + '\' from the input file'
else:
    print >>sys.stderr, 'Finding occurences of \'' + error_string + '\' in the input file'


# compile the error string into a regex object
error_re = re.compile(error_string)


line = sys.stdin.readline()
while line:
    if re.match('FAIL:', line):
        match_buffer = str(line)
        line = sys.stdin.readline()

        buffering = True
        while buffering:
            # stop at eof or when the next block is encountered
            if not line:
                buffering = False
            if re.match('(FAIL|PASS|UNRESOLVED):', line):
                buffering = False
            else:
                match_buffer += line
                line = sys.stdin.readline()

        # output a match if we are not filtering 
        match = error_re.search(match_buffer)
        if (not filtering) and match:
            sys.stdout.write(match_buffer)
        elif filtering and (not match):
            sys.stdout.write(match_buffer)
    else:
        if filtering:
            sys.stdout.write(line)
        line = sys.stdin.readline()
