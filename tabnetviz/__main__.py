#!/usr/bin/env python3

'''tabnetviz main module'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html

# standard imports
import sys
import os
import argparse
from time import sleep
from collections import OrderedDict, Counter

# 3rd party imports
import yaml
import yamlloader
import pygraphviz as pgv
import pandas as pd
from matplotlib import cm, colors

# own imports
from tabnetviz import __version__
from tabnetviz.gvattrs import gvattrs
from tabnetviz import netanalyzer
from tabnetviz import colorbarsvg
from tabnetviz import configtemplate
from tabnetviz.kwcheck import kwcheck


def parseconfig(fname):
    '''parse yaml configuration file'''
    f = open(fname)
    yamlloader.settings.PY_LE_36 = True # otherwise loads dict instead of ordereddict
    conf = yaml.load(f, Loader=yamlloader.ordereddict.CLoader)
    f.close()
    return conf

def tovarname(s):
    '''convert column name to variable name'''
    s = str(s)
    v = ''.join([c for c in s if c.isalnum() or c == '_'])
    if v[0].isdigit():
        v = 'c'+v
    return v

def checkkeywords(conf):
    '''check whether all config keywords are valid'''
    s = 'networktype title layout graphattrs networkanalysis nodegroups edgegroups clusters'
    top0kw = s.split() # toplevel keywords with no subkeywords
    xtable = 'filetype file sheet noheader'.split()
    etable = xtable+'sourcecolumn targetcolumn fromcytoscape'.split()
    ntable = xtable+'idcolumn skipisolated'.split()
    # toplevel keywords with children
    top1kw = {'edgetable': etable,
              'nodetable': ntable,
              'outputfiles': 'drawing dot nodetableout edgetableout colorbars'.split(),
              'remove': ['nodes', 'edges', 'keepisolatednodes']}
    # toplevel keywords with grandkids
    top2kw = {'addrankings': 'table colexpr method reverse withingroup'.split(),
              'colormaps': 'type map'.split()}
    # toplevel keywords with grandgrandkids (too complex)
    top3kw = 'nodestyles edgestyles'.split()
    # check for all toplevel keywords
    kwcheck(conf, top0kw+list(top1kw)+list(top2kw)+top3kw, context=' in config file')
    # check top1kw keywords
    for kw in top1kw:
        if kw in conf and type(conf[kw]) == OrderedDict:
            kwcheck(conf[kw], top1kw[kw], context=' in config file under '+kw)
    # check top2kw keywords
    for kw in top2kw:
        if kw in conf and type(conf[kw]) == OrderedDict:
            for kww in conf[kw]:
                if type(conf[kw][kww]) == OrderedDict:
                    kwcheck(conf[kw][kww], top2kw[kw], context=' in config file under '+kw+'/'+kww)
    # check top3kw keywords
    typekw = {'direct': ['colexpr'],
              'discrete': 'colexpr map'.split(),
              'linear': 'colexpr colmin colmax mapmin mapmax withingroup'.split(),
              'cont2disc': 'colexpr map'.split(),
              'colormap': 'colexpr colmin colmax centerzero colormap reverse withingroup'.split(),
              'combine': 'attrlist formatstring'.split()}
    for kw in top3kw:
        if kw in conf and type(conf[kw]) == OrderedDict:
            for groupname in conf[kw]:
                if type(conf[kw][groupname]) == OrderedDict:
                    for attrname in conf[kw][groupname]:
                        if type(conf[kw][groupname][attrname]) == OrderedDict:
                            ct = ' in config file under '+'/'.join([kw, groupname, attrname])
                            if 'type' not in conf[kw][groupname][attrname]:
                                raise ValueError('type parameter missing in '+ct)
                            tp = conf[kw][groupname][attrname]['type']
                            ct += ' (type: '+tp+')'
                            validkw = ['type']+typekw[tp]
                            kwcheck(conf[kw][groupname][attrname], validkw, context=ct)

def cont2disc(x, cdmap):
    '''continuous-to-discrete mapping function'''
    for h in list(cdmap)[:-1]:
        if x <= h:
            return cdmap[h]
    return cdmap['higher']
        
def table2net(args):
    '''create visualization'''
    configfile = args.configfile
    conf = parseconfig(configfile)
    checkkeywords(conf) # do some input validation
    
    # read input files (edge and node table)
    
    sepchar = {'csv': ',', 'tsv': '\t'}

    # load edge table
    if args.edgetable: # file name specified on command line
        if 'edgetable' not in conf:
            conf['edgetable'] = {'file': args.edgetable}
        else:
            conf['edgetable']['file'] = args.edgetable
    if type(conf['edgetable']) == str: # only a filename is provided
        conf['edgetable'] = {'file': conf['edgetable']}
    etfile = conf['edgetable']['file']
    header = None if conf['edgetable'].get('noheader', False) else 0
    
    if 'filetype' in conf['edgetable']:
        ftype = conf['edgetable']['filetype']
    elif etfile[-4:].lower() == '.csv':
        ftype = 'csv'
    elif etfile[-4:].lower() == '.tsv':
        ftype = 'tsv'
    elif ntfile[-5:].lower() == '.xlsx' or ntfile[-4:].lower() == '.xls':
        ftype = 'xlsx'
        
    if ftype in ['csv', 'tsv']:
        edgetab = pd.read_csv(etfile, sep=sepchar[ftype], header=header)
    elif ftype in ['xlsx', 'xls']:
        edgetab = pd.read_excel(etfile, header=header, 
          sheet_name=conf['edgetable'].get('sheet', 0))
    else:
        raise ValueError('Unknown edge table file type: %s' % (ftype))
    
    if conf['edgetable'].get('fromcytoscape', False):
        # for edge table exported from Cytoscape, separate source and target
        srctarlist = [edgetab.at[x, 'name'].split(' ('+edgetab.at[x, 'interaction']+') ')
          for x in edgetab.index]
        edgetab['source'] = [src for [src, tar] in srctarlist]
        edgetab['target'] = [tar for [src, tar] in srctarlist]
        
    if header == None:
        edgetab.columns = ['col'+str(j) for j in range(1, edgetab.shape[1]+1)]
        sourcecolumn = 'col1'
        targetcolumn = 'col2'
    else:
        sourcecolumn = conf['edgetable'].get('sourcecolumn', edgetab.columns[0])
        targetcolumn = conf['edgetable'].get('targetcolumn', edgetab.columns[1])
        
    if sourcecolumn not in edgetab.columns:
        raise ValueError('Column "%s" not found in edge table' % (sourcecolumn))
    if targetcolumn not in edgetab.columns:
        raise ValueError('Column "%s" not found in edge table' % (targetcolumn))
    
    # set of nodes with edges
    nodesfromedges = set(edgetab[sourcecolumn]) | set(edgetab[targetcolumn])
    
    # load node table
    if 'nodetable' not in conf and not args.nodetable:
        # infer node table from edge table
        nodes = set(edgetab[sourcecolumn]) | set(edgetab[targetcolumn])
        nodetab = pd.DataFrame()
        nodetab['name'] = list(nodes)
        nodetab.index = list(nodetab['name'])
        idcolumn = 'name'
    else:
        if args.nodetable: # file specified on command line
            if 'nodetable' not in conf:
                conf['nodetable'] = {'file': args.nodetable}
            else:
                conf['nodetable']['file'] = args.nodetable
        if type(conf['nodetable']) == str:
            conf['nodetable'] = {'file': conf['nodetable']} # only a filename is given
        ntfile = conf['nodetable']['file']
        header = None if conf['nodetable'].get('noheader', False) else 0
        if 'filetype' in conf['nodetable']:
            ftype = conf['nodetable']['filetype']
        elif ntfile[-4:].lower() == '.csv':
            ftype = 'csv'
        elif ntfile[-4:].lower() == '.tsv':
            ftype = 'tsv'
        elif ntfile[-5:].lower() == '.xlsx' or ntfile[-4:].lower() == '.xls':
            ftype = 'xlsx'
        if ftype in ['csv', 'tsv']:
            nodetab = pd.read_csv(ntfile, sep=sepchar[ftype], header=header)
        elif ftype in ['xlsx', 'xls']:
            nodetab = pd.read_excel(ntfile, header=header, 
              sheet_name=conf['nodetable'].get('sheet', 0))
        else:
            raise ValueError('Unknown node table file type: %s' % (ftype))
        idcolumn = conf['nodetable'].get('idcolumn', nodetab.columns[0])
        if idcolumn not in nodetab.columns:
            raise ValueError('Column "%s" not found in node table' % (idcolumn))
        # delete isolated nodes if requested
        if conf['nodetable'].get('skipisolated', False):
            xtodrop = nodetab.query(idcolumn+' not in @nodesfromedges').index
            nodetab.drop(xtodrop, inplace=True)
        # check for duplicate node names
        c = Counter(list(nodetab[idcolumn]))
        dup = [e for e in c if c[e] > 1]
        if dup:
            raise ValueError('Duplicate node names: %s' % (' '.join(map(str, dup))))
        nodetab.index = list(nodetab[idcolumn])
    
    # convert column names to variable names
    
    nodetab.columns = [tovarname(cname) for cname in nodetab.columns]
    edgetab.columns = [tovarname(cname) for cname in edgetab.columns]
    idcolumn = tovarname(idcolumn)

    # set drawing output file
    
    if 'outputfiles' not in conf:
        conf['outputfiles'] = {'drawing': 'out.svg'}
    elif type(conf['outputfiles']) == str:
        conf['outputfiles'] = {'drawing': conf['outputfiles']}
    elif type(conf['outputfiles']) == OrderedDict and 'drawing' not in conf['outputfiles']:
        conf['outputfiles']['drawing'] = 'out.svg'

    if args.output: # drawing output file specified on command line
        conf['outputfiles']['drawing'] = args.output

    # set optional node and edge table output files from command line
    
    if args.nodetableout:
        conf['outputfiles']['nodetableout'] = args.nodetableout
    if args.edgetableout:
        conf['outputfiles']['edgetableout'] = args.edgetableout

    # remove nodes and edges if requested
    
    if 'remove' in conf:
        # remove nodes
        if 'nodes' in conf['remove']:
            x = nodetab.query(conf['remove']['nodes']).index
            S = set(nodetab.loc[x, idcolumn]) # set of nodes to remove
            nodetab.drop(index=x, inplace=True) # delete nodes
            y = edgetab.query(sourcecolumn+' in @S or '+targetcolumn+' in @S').index
            # delete edges belonging to the deleted nodes
            edgetab.drop(index=y)
        # remove edges
        if 'edges' in conf['remove']: # remove edges
            x = edgetab.query(conf['remove']['edges']).index
            # set of nodes connected by the edges to remove
            S = set(edgetab.loc[x, sourcecolumn]) | set(edgetab.loc[x, targetcolumn])
            edgetab.drop(index=x, inplace=True) # delete edges
            # remove nodes that have become isolated after edge removal 
            # unless keeping them is requested
            keep = conf['remove'].get('keepisolatednodes', False)
            if not keep:
                nonisol = set(edgetab.loc[:, sourcecolumn]) | set(edgetab.loc[:, targetcolumn])
                becameisol = S-nonisol # became isolated due to the edge removal
                x = nodetab.query(idcolumn+' in @becameisol').index
                nodetab.drop(index=x, inplace=True) # delete these
                
    # perform network analysis if requested
    
    directed = conf.get('networktype', 'undirected') == 'directed'
    
    if conf.get('networkanalysis', False):
        # perform network analysis
        (nodeqdic, edgeqdic) = netanalyzer.calcquant(nodetab, idcolumn, edgetab, sourcecolumn, 
          targetcolumn, directed, quant=conf.get('networkanalysis'))
        # add the new columns to node table and edge table
        for q in nodeqdic:
            nodetab[q] = nodeqdic[q]
        for q in edgeqdic:
            edgetab[q] = edgeqdic[q]
    
    # create pygraphviz graph object
    
    G = pgv.AGraph(name='network', directed=conf.get('networktype', 'undirected') == 'directed', 
      strict=False)
    
    for nodename in nodetab[idcolumn]:
        G.add_node(nodename)
    
    for x in edgetab.index:
        G.add_edge(edgetab[sourcecolumn][x], edgetab[targetcolumn][x], key=x)
    
    # if input dot is specified, read it and check if nodes/edges are the same as G
    
    if conf.get('layout', 'neato').lower().endswith('.dot'):
        L = pgv.AGraph(conf['layout'])
        Ge = G.edges(keys=True)
        Le = L.edges(keys=True)
        Gn = G.nodes()
        Ln = L.nodes()
        if (len(Ge), len(Gn), set(Ge), set(Gn)) == (len(Le), len(Ln), set(Le), set(Ln)):
            if (all('pos' in L.get_node(v).attr for v in L.nodes()) and 
                all('pos' in L.get_edge(u, v, key=x).attr for (u, v, x) in L.edges(keys=True))):
                # copy all positions
                for v in Ln:
                    vG = G.get_node(v)
                    vL = L.get_node(v)
                    vG.attr['pos'] = vL.attr['pos']
                for (u, v, x) in Le:
                    eG = G.get_edge(u, v, key=x)
                    eL = L.get_edge(u, v, key=x)
                    eG.attr['pos'] = eL.attr['pos']
                G.has_layout = True
            else:
                raise ValueError('graph in the input dot file %s has no layout information' %
                                  (conf['layout']))
        else:
            raise ValueError('graph in the input dot file %s differs from the graph specified '
                             'in the tables' % (conf['layout']))
    elif conf.get('layout', 'neato') not in ['neato', 'dot', 'twopi', 'circo', 'fdp', 'sfdp',
                  'patchwork', 'osage']:
        raise ValueError('layout should be one of neato, dot, twopi, circle, fdp, sfdp, '
                         'patchwork, or a .dot file name')
        
    
    # parse graph attribute definitions
    
    ## by default, use outputorder=edgesfirst, overlap=false
    G.graph_attr['outputorder'] = 'edgesfirst'
    G.graph_attr['overlap'] = False
    # check validity of graph attribute names
    kwcheck(conf.get('graphattrs', []), gvattrs['G'], name='graph attribute|graph attributes')
    for gattr in conf.get('graphattrs', []):
        G.graph_attr[gattr] = conf['graphattrs'][gattr]
    
    # parse node group definitions
    
    nodegroups = OrderedDict()
    nodegroups['default'] = nodetab.index
    if 'nodegroups' in conf:
        for ngname in conf['nodegroups']:
            if ngname in nodetab.columns:
                if nodetab[ngname].dtype == bool:
                    # group name matches a Boolean column name, accept it as a group
                    nodegroups[ngname] = nodetab.query(ngname).index
                    continue
                else:
                    raise ValueError('node group name %s matches existing node table column name' %
                      (ngname))
            groupdef = conf['nodegroups'][ngname]
            # add boolean column to node table so the group can be used in subsequent
            # group definitions
            if type(groupdef) == str:
                nodetab[ngname] = nodetab.eval(groupdef, engine='python')
            elif type(groupdef) == list: # explicit node list given
                NS = set(groupdef) # node set
                U = NS-set(nodetab.index)
                if U: # there are unknown node names
                    raise ValueError('unknown node(s) given in node group definition: '+str(U))
                nodetab[ngname] = nodetab.eval(idcolumn+' in @NS', engine='python')
            else:
                raise ValueError('group definition must be string or list: '+ngname)
            nodegroups[ngname] = nodetab.query(ngname, engine='python').index
                    
    # parse edge group definitions
    
    edgegroups = OrderedDict()
    edgegroups['default'] = edgetab.index
    if 'edgegroups' in conf:
        for egname in conf['edgegroups']:
            if egname in edgetab.columns:
                if edgetab[egname].dtype == bool:
                    # group name matches a Boolean column name, accept it as a group
                    edgegroups[egname] = edgetab.query(egname).index
                    continue
                else:
                    raise ValueError('edge group name %s matches existing edge table column name' %
                      (egname))
            groupdef = conf['edgegroups'][egname]
            # add boolean column to node table so the group can be used in subsequent
            # group definitions
            if type(groupdef) == str:
                edgetab[egname] = edgetab.eval(groupdef, engine='python')
            elif type(groupdef) == list: # explicit edge list given
                edges = list(zip(edgetab[sourcecolumn], edgetab[targetcolumn]))
                ES = set(groupdef)
                U = ES-set(edges)
                if U: # there are unknown edges given
                    raise ValueError('unknown edges specified in edge group definition: '+str(U))
                edgetab[egname] = [e in ES for e in edges] # adding Boolean column to edge table
            edgegroups[egname] = edgetab.query(egname, engine='python').index
    
    # parse cluster definitions
    
    if 'clusters' in conf:
        if type(conf['clusters']) == str:
            conf['clusters'] = [conf['clusters']]
        if conf.get('layout', 'neato') not in ['dot', 'fdp']:
            raise ValueError('Only dot and fdp support clusters.')
        if type(conf['clusters']) == OrderedDict: # dict was provided, not list
            # convert dict to list
            conf['clusters'] = [OrderedDict({g: conf['clusters'][g] if conf['clusters'][g] 
              else OrderedDict()}) for g in conf['clusters']]
        # make a dictionary for clusters
        clusdefs = OrderedDict()
        for clusdef in conf['clusters']:
            if type(clusdef) == str:
                if clusdef not in nodegroups:
                    raise ValueError('No such node group: '+clusdef)
                clusdefs[clusdef] = OrderedDict() # no attributes provided, empty dic
            elif type(clusdef) == OrderedDict:
                clusname = list(clusdef)[0]
                if clusname not in nodegroups:
                    raise ValueError('No such node group: '+clusname)
                clusdefs[clusname] = clusdef[clusname] # attributes dictionary
                # check validity of attribute names
                kwcheck(list(clusdefs[clusname]), gvattrs['C'],
                  name='cluster attribute|cluster attributes', context=' in cluster '+clusname)
            else:
                print(clusdef, type(clusdef))
                raise ValueError('Clusters must be node group names with/without attributes')
        # make node sets out of clusters
        clusnodesets = OrderedDict((ngname, set(nodegroups[ngname])) for ngname in clusdefs)
        clusnames = list(clusdefs) # cluster names = node group names
        nclus = len(clusdefs)
        # check clusters (node groups) for overlaps/containment
        # any two clusters must either be disjoint, or one must be a proper subset of the other
        for i in range(nclus-1):
            seti = clusnodesets[clusnames[i]]
            for j in range(i+1, nclus):
                setj = clusnodesets[clusnames[j]]
                if not (seti & setj == set() or seti < setj or setj < seti):
                    raise ValueError('Overlapping/identical clusters are not allowed (%s-%s)' % 
                      (clusnames[i], clusnames[j]))
        # find parent each cluster: smallest cluster containing it
        parent = {}
        children = {c: [] for c in clusnames} # children of a cluster
        children['_top'] = [] # toplevel cluster (=root graph, not a cluster)
        for clusname in clusnames:
            ancestors = [c for c in clusnodesets if clusnodesets[c] > clusnodesets[clusname]]
            if ancestors == []:
                parent[clusname] = '_top' # no parent (toplevel cluster)
                # add to children of toplevel cluster
                children['_top'].append(clusname)
            else:
                # pick smallest ancestor as parent
                parent[clusname] = min(ancestors, key=lambda c: len(clusnodesets[c]))
                # the parent has clusname as child
                children[parent[clusname]].append(clusname)
        # we have the cluster tree; traverse it by DFS from root, and create the subgraphs
        subgraphs = {'_top': G}
        S = ['_top'] # stack
        while S:
            v = S.pop()
            if v != '_top':
                P = subgraphs[parent[v]]
                C = P.add_subgraph(clusnodesets[v], name='cluster_'+v, **clusdefs[v])
                subgraphs[v] = C
            S += children[v]
        
    # parse addrankings
    
    if 'addrankings' in conf:
        for columnname in conf['addrankings']:
            tt = conf['addrankings'][columnname]
            if tt['table'] == 'nodetable':
                tab = nodetab
                withingroup = nodegroups[tt.get('withingroup', 'default')]
            elif tt['table'] == 'edgetable':
                tab = edgetab
                withingroup = edgegroups[tt.get('withingroup', 'default')]
            else:
                raise ValueError('Invalid value of addrankings table: %s' % (t))
            method = tt.get('method', 'average')
            reverse = not tt.get('reverse', False)
            # add new column to table
            tab[columnname] = tab.loc[withingroup].eval(tt['colexpr']).rank(method=method, 
              ascending=reverse)
    
    # parse custom colormaps
    
    if 'colormaps' in conf:
        for colormapname in conf['colormaps']:
            tt = conf['colormaps'][colormapname]
            if tt['type'] == 'discrete':
                tt['colormap'] = colors.ListedColormap(tt['map'], name=colormapname)
            elif tt['type'] == 'continuous':
                tt['colormap'] = colors.LinearSegmentedColormap.from_list(colormapname,
                  list(tt['map'].items()))
            else:
                raise ValueError('No such colormap type: '+tt['type'])
    
    # parse node and edge styles

    # for colorbars output, if requested
    cbs = False
    if 'colorbars' in conf['outputfiles']:
        cbs = colorbarsvg.ColorBars()
    # move default group to start of list
    if 'default' in conf.get('nodestyles', {}):
        conf['nodestyles'].move_to_end('default', last=False)
    if 'default' in conf.get('edgestyles', {}):
        conf['edgestyles'].move_to_end('default', last=False)
    # iterate over groups
    for igr, gr in enumerate(list(conf.get('nodestyles', []))+list(conf.get('edgestyles', []))):
        isnodegr = igr < len(conf.get('nodestyles', []))
        isedgegr = not isnodegr
        tab = nodetab if isnodegr else edgetab
        if isnodegr and gr not in nodegroups:
            raise ValueError('Undefined node group: '+gr)
        elif isedgegr and gr not in edgegroups:
            raise ValueError('Undefined edge group: '+gr)
        xlist = nodegroups[gr] if isnodegr else edgegroups[gr]
        confst = conf['nodestyles' if isnodegr else 'edgestyles']
        props = confst[gr]
        gvattrsg = gvattrs['N'] if isnodegr else gvattrs['E']
        gname = 'node' if isnodegr else 'edge'
        # check for valid attribute names
        gvprops = [prop for prop in props if not prop.startswith('ng')]
        kwcheck(gvprops, gvattrsg, name=gname+' attribute|'+gname+' attributes',
          context=' under '+gname+'styles/'+gr)
        # iterate over attributes
        for prop in props:
            propval = props[prop] # attribute value
            # constant value "mapping"
            if type(propval) != OrderedDict: # constant value for property (=attribute)
                if gr == 'default': # default value
                    if prop.startswith('ng'): # non-graphviz property
                        tab[prop] = propval
                    elif isnodegr:
                        G.node_attr[prop] = propval
                    else:
                        G.edge_attr[prop] = propval
                else: # a non-default group
                    for x in xlist:
                        if prop.startswith('ng'): # non-graphviz property
                            tab.loc[x, prop] = propval
                        elif isnodegr: # for node table
                            node = G.get_node(x)
                            node.attr[prop] = propval
                        else: # for edge table
                            edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], 
                              key=x)
                            edge.attr[prop] = propval
            # direct mapping
            elif propval['type'] == 'direct': # direct mapping of table data to style
                col = tab.eval(propval['colexpr'], engine='python')
                for x in xlist:
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = col[x]
                    elif isnodegr: # for node table
                        node = G.get_node(x)
                        node.attr[prop] = col[x]
                    else: # for edge table
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = col[x]
            # discrete mapping
            elif propval['type'] == 'discrete': # discrete mapping
                col = tab.eval(propval['colexpr'], engine='python')
                for x in xlist:
                    if col[x] not in propval['map']:
                        continue
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = propval['map'][col[x]]
                    elif isnodegr: # for node table
                        node = G.get_node(x)
                        node.attr[prop] = propval['map'][col[x]]
                    else: # for edge table
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = propval['map'][col[x]]
            # linear mapping
            elif propval['type'] == 'linear': # linear mapping
                col = tab.eval(propval['colexpr'], engine='python')
                if propval.get('withingroup', False):
                    minval = col[xlist].dropna().min()
                    maxval = col[xlist].dropna().max()
                else:
                    minval = col.dropna().min()
                    maxval = col.dropna().max()
                minval = propval.get('colmin', minval)
                maxval = propval.get('colmax', maxval)
                mapmin = propval['mapmin']
                mapmax = propval['mapmax']
                factor = (mapmax-mapmin)/(maxval-minval)
                col = mapmin+factor*(col-minval)
                for x in xlist:
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = col[x]
                    elif isnodegr:
                        node = G.get_node(x)
                        node.attr[prop] = col[x]
                    else:
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = col[x]
            # cont2disc mapping
            elif propval['type'] == 'cont2disc': # continuous-to-discrete mapping
                col = tab.eval(propval['colexpr'], engine='python')
                L = list(propval['map'])
                if L[-1] != 'higher':
                    raise ValueError('last value in cont2disc map must be "higher"')
                if sorted(L[:-1]) != L[:-1]:
                    raise ValueError('values in cont2disc map must be in ascending order')
                for x in xlist:
                    mappedval = cont2disc(col[x], propval['map'])
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = mappedval
                    elif isnodegr:
                        node = G.get_node(x)
                        node.attr[prop] = mappedval
                    else:
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = mappedval
            # colormap mapping
            elif propval['type'] == 'colormap': # color mapping
                col = tab.eval(propval['colexpr'], engine='python').copy()
                if 'colormaps' in conf and propval['colormap'] in conf['colormaps']:
                    cmap = conf['colormaps'][propval['colormap']]['colormap']
                else:
                    cmap = cm.get_cmap(propval['colormap'])
                rev = propval.get('reverse', False)
                if propval.get('withingroup', False):
                    minval = col[xlist].dropna().min()
                    maxval = col[xlist].dropna().max()
                else:
                    minval = col.dropna().min()
                    maxval = col.dropna().max()
                minval = propval.get('colmin', minval)
                maxval = propval.get('colmax', maxval)
                if propval.get('centerzero', False):
                    if minval*maxval > 0: # min and max are of the same sign
                        raise ValueError('Data range %s for colormap does not include zero; '
                            'centerzero is not possible.' % (propval['colexpr']))
                    if propval['centerzero'] == 'aligncloser':
                        if abs(minval) < abs(maxval): # minval is closer to zero
                            factor = abs(0.5/minval)
                            col = factor*(col-minval)
                            if cbs:
                                r = factor*(maxval-minval)
                                print(propval['colexpr'], 'right', factor*(maxval-minval))
                                cbs.add(cmap, minval=minval, maxval=maxval, reverse=rev,
                                  right=1.0/r, center=0.5/r, title=propval['colexpr'])
                        else: # maxval is closer to zero
                            factor = abs(0.5/maxval)
                            col = factor*col+0.5
                            if cbs:
                                r = factor*(maxval-minval)
                                cbs.add(cmap, minval=minval, maxval=maxval, reverse=rev,
                                  center=1.0-0.5/r, left=1.0-1.0/r, title=propval['colexpr'])
                    elif propval['centerzero'] == 'alignfarther':
                        if abs(minval) > abs(maxval): # minval is farther from zero
                            factor = abs(0.5/minval)
                            col = factor*(col-minval)
                            if cbs:
                                r = factor*(maxval-minval)
                                cbs.add(cmap, minval=minval, maxval=maxval, reverse=rev,
                                  right=1.0/r, center=0.5/r, title=propval['colexpr'])
                        else:
                            factor = abs(0.5/maxval)
                            col = factor*col+0.5
                            if cbs:
                                r = factor*(maxval-minval)
                                cbs.add(cmap, minval=minval, maxval=maxval, reverse=rev,
                                  center=1.0-0.5/r, left=1.0-1.0/r, title=propval['colexpr'])
                    elif propval['centerzero'] == 'piecewise':
                        xneg = col < 0
                        xpos = col >= 0
                        col[xneg] = 0.5/abs(minval)*(col[xneg]-minval)
                        col[xpos] = 0.5/abs(maxval)*col[xpos]+0.5
                        if cbs:
                            cbs.add(cmap, minval=minval, maxval=maxval, title=propval['colexpr'],
                              center=abs(minval)/(abs(minval)+abs(maxval)), reverse=rev)
                else:
                    factor = 1.0/(maxval-minval)
                    col = factor*(col-minval)
                    if cbs:
                        cbs.add(cmap, minval=minval, maxval=maxval, title=propval['colexpr'], 
                          reverse=rev)
                if rev:
                    col = 1.0-col
                for x in xlist:
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = colors.to_hex(cmap(col[x]), keep_alpha=True)
                    elif isnodegr:
                        node = G.get_node(x)
                        node.attr[prop] = colors.to_hex(cmap(col[x]), keep_alpha=True)
                    else:
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = colors.to_hex(cmap(col[x]), keep_alpha=True)
            # combine mapping
            elif propval['type'] == 'combine':
                for x in xlist:
                    t = tuple([tab.at[x, p] for p in propval['attrlist']])
                    s = propval['formatstring'] % t
                    if prop.startswith('ng'): # non-graphviz property
                        tab.at[x, prop] = s
                    elif isnodegr:
                        node = G.get_node(x)
                        node.attr[prop] = s
                    else:
                        edge = G.get_edge(tab.at[x, sourcecolumn], tab.at[x, targetcolumn], key=x)
                        edge.attr[prop] = s
            # unknown mapping type
            else:
                raise ValueError('Unknown property mapping type: %s' % (propval['type']))
    
    # output dot; draw the graph
    
    layout = conf.get('layout', 'neato')
    if not layout.lower().endswith('.dot'):
        print('Laying out graph...') # may take some time
        G.layout(prog=layout)
    
    outputfiles = conf['outputfiles']
    drawout = outputfiles['drawing']
    print('Writing output files...')
    # write drawing
    G.draw(drawout)
    print('Drawing written to', drawout)
    # write dot file if requested
    if 'dot' in outputfiles:
        G.write(outputfiles['dot']) # write dot file
        print('Dot file written to', outputfiles['dot'])
    # write node table if requested
    if 'nodetableout' in outputfiles:
        fname = outputfiles['nodetableout']
        if 'nodetable' in conf and ntfile == fname:
            raise ValueError('Cannot overwrite node table file')
        sep = sepchar.get(fname.lower()[-3:], False)
        if sep:
            nodetab.to_csv(fname, sep=sep, index=False)
        elif fname.lower().endswith('xls') or fname.lower().endswith('xlsx'):
            nodetab.to_excel(fname, index=False)
        print('Modified node table written to', fname)
    # write edge table if requested
    if 'edgetableout' in outputfiles:
        fname = outputfiles['edgetableout']
        if etfile == fname:
            raise ValueError('Cannot overwrite edge table file')
        sep = sepchar.get(fname.lower()[-3:], False)
        if sep:
            edgetab.to_csv(fname, sep=sep, index=False)
        elif fname.lower().endswith('xls') or fname.lower().endswith('xlsx'):
            edgetab.to_excel(fname, index=False)
        print('Modified edge table written to', fname)
    # write colorbars if requested
    if cbs:
        fname = conf['outputfiles']['colorbars']
        cbs.writesvg(fname)
        print('Colorbars written into', fname)
            

## Main program

def main():
    # parse arguments
    epi = 'Tabnetviz v'+__version__+'. See https://git.io/tabnetviz for documentation.'
    epi += ' Copyright 2019 Andras Szilagyi. Distributed under GNU GPL version 3.'
    parser = argparse.ArgumentParser(description='Table-based network visualizer', epilog=epi)
    parser.add_argument('-w', '--watch', action='store_true', 
      help='Watch the config file and re-run upon detecting a change')
    parser.add_argument('-n', '--nodetable', help='node table file name')
    parser.add_argument('-e', '--edgetable', help='edge table file name')
    parser.add_argument('-o', '--output', help='output file for the drawing')
    parser.add_argument('--nodetableout', help='file name for writing modified node table')
    parser.add_argument('--edgetableout', help='file name for writing modified edge table')
    parser.add_argument('--configtemplate', action='store_true',
      help='Write a configuration template to the specified file and exit')
    parser.add_argument('configfile', help='Configuration file')
    a = parser.parse_args()

    # write config file template if requested
    if a.configtemplate:
        if os.path.exists(a.configfile):
            # do not overwrite
            print('Configuration file already exists, will not overwrite:', a.configfile)
            print('Delete the file or provide a different filename')
        else:
            fw = open(a.configfile, 'wt')
            fw.write(configtemplate.template)
            fw.close()
        sys.exit()
    
    # create visualization
    table2net(a)
    
    # watch if -w is given
    if a.watch:
        print('Watching config file (%s) for changes, press Ctrl-C to quit...' % (a.configfile))
        mtime = os.stat(a.configfile).st_mtime
        while True:
            sleep(0.5)
            mt = os.stat(a.configfile).st_mtime
            if mt != mtime:
                print('Re-running...')
                try:
                    table2net(a.configfile)
                except ValueError as e:
                    print('ValueError:', e)
                mtime = mt

if __name__ == '__main__':
    main()
