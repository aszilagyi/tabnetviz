'''check words against a set of valid words, provide suggestions'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import difflib

def kwcheck(keywords, validkeywords, name='keyword|keywords', context=''):
    '''report unknown keywords and provide suggestions'''
    U = set(keywords)-set(validkeywords)
    if U:
        name1, names = name.split('|')
        what = names if len(U) > 1 else name1
        print('Unknown %s%s:' % (what, context), file=sys.stderr)
        nosugg = False
        for kw in U:
            sugg = difflib.get_close_matches(kw, list(validkeywords), n=1)
            if sugg:
                print('"'+kw+'": did you mean "'+sugg[0]+'"?', file=sys.stderr)
            else:
                print('"'+kw+'"', file=sys.stderr)
                nosugg = True
        if nosugg:
            print('Valid %s are:' % (names), ', '.join(sorted(validkeywords)), file=sys.stderr)
        sys.exit(1)
    
