'''network analyzer for tabnetviz'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html
#
# Thanks to Zsofia Feher for an initial version of this module

import sys
import difflib
from collections import OrderedDict

import networkx as nx
import pandas as pd

from tabnetviz.kwcheck import kwcheck
        
def Degree(G):
    return G.degree

def Indegree(G):
    return G.in_degree

def Outdegree(G):
    return G.out_degree

def Connectivity(G):
    '''number of neighbors of a node (can differ from Degree which is the number of edges)'''
    H = nx.to_undirected(G).copy() # convert to undirected
    R = list(nx.selfloop_edges(H))
    for (u, v) in R:
        H.remove_edge(u, v) # remove self-loop edges
    conn = {v: len(H.adj[v]) for v in H} # connectivity (=number of neighbors)
    return conn

def BetweennessCentrality(G):
    # we normalize separately for each connected component
    bc_nonnorm = nx.betweenness_centrality(G, normalized=False)
    S = list(nx.connected_components(nx.to_undirected(G)))
    f = 1 if G.is_directed() else 2
    normf = [0 if len(c) in [1, 2] else f/(len(c)-1)/(len(c)-2) for c in S]
    compdic = {v: j for (j, H) in enumerate(S) for v in H}
    bc_norm = {v: bc_nonnorm[v]*normf[compdic[v]] for v in bc_nonnorm}
    return bc_norm

def ClosenessCentrality(G):
    if not G.is_directed():
        return nx.closeness_centrality(G, wf_improved=False)
    return nx.closeness_centrality(G.reverse(), wf_improved=False)

def ClusteringCoefficient(G):
    # NOTE: clustering coefficient definition for directed networks is slightly
    # different in Networkx than in Cytoscape's Network Analyzer
    # thus, numerical results will be slightly different for some of the nodes.
    # We stick to Networkx here.
    if G.is_multigraph(): # clustering coefficient not implemented for multigraphs
        print('Warning: Converting multi-graph to simple for clustering coefficient calculation')
        H = nx.DiGraph(G) if G.is_directed() else nx.Graph(G) # convert to non-multi
        return nx.clustering(H)
    return nx.clustering(G)

def Eccentricity(G):
    # networkx implementation throws error for disconnected/not strongly connected graphs
    # so re-implement like NetworkAnalyzer
    col = {v: max(dic.values()) for (v, dic) in nx.all_pairs_shortest_path_length(G)}
    return col

def NeighborhoodConnectivity(G):
    H = nx.to_undirected(G).copy() # convert to undirected
    R = list(nx.selfloop_edges(H))
    for (u, v) in R:
        H.remove_edge(u, v) # remove self-loop edges
    conn = {v: len(H.adj[v]) for v in H} # connectivity (=number of neighbors)
    return {v: sum(conn[n]/conn[v] for n in H.neighbors(v)) for v in G}
    
def AverageShortestPathLength(G):
    col = {}
    dicdic = dict(nx.all_pairs_shortest_path_length(G))
    for v in G.nodes:
        dic = dicdic[v]
        n = len(dic)
        if n == 1:
            col[v] = 0.0 # isolated node
        else:
            col[v] = sum(dic.values())/(n-1)
    return col

def Radiality(G):
    avsp = AverageShortestPathLength(G)
    S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
    dia = [nx.diameter(H) for H in S]
    compdic = {v: j for (j, H) in enumerate(S) for v in H}
    vdia = {v: dia[compdic[v]] for v in G}
    rad = {v: float('inf') if vdia[v] == 0 else (vdia[v]-avsp[v]+1)/vdia[v] for v in G}
    return rad
    
def EdgeBetweenness(G):
    ebc = nx.edge_betweenness_centrality(G, normalized=False)
    if G.is_directed():
        return ebc
    return {v: 2*ebc[v] for v in ebc}

def SelfLoops(G):
    return {v: list(G.edges()).count((v, v)) for v in G.nodes}

def Stress(G):
    # shortest paths
    paths = []
    # v is part of how many shortest paths
    for u in G:
        for v in G:
            if v == u:
                continue
            if not nx.has_path(G, u, v):
                continue
            for path in nx.all_shortest_paths(G, u, v):
                paths.append(path[1:-1])
    col = {v: [v in path for path in paths].count(True) for v in G}
    return col

def TopologicalCoefficient(G):
    # remove self-loops
    H = G.copy()
    R = list(nx.selfloop_edges(H))
    for (u, v) in R:
        H.remove_edge(u, v) # remove self-loop edges
    # average number of shared neighbors with other nodes
    col = {}
    for n in H: # iterate on nodes
        kn = len(H.adj[n]) # number of neighbors (!= degree for multigraphs)
        if kn in [0, 1]:
            col[n] = 0
            continue
        nneib = set(H.neighbors(n))
        Nm = 0
        sumshared = 0
        for m in H: # iterate on other nodes
            if m == n:
                continue
            mneib = set(H.neighbors(m))
            numshared = len(nneib & mneib)
            if numshared > 0: # if n and m have shared neighbors
                Nm += 1
                if m in nneib:
                    numshared += 1 # add 1 if n and m are neighbors
                sumshared += numshared
        avg = sumshared/Nm if Nm > 0 else 0
        col[n] = avg/kn
    return col

def calcquant(nodetab, idcol, edgetab, sourcecol, targetcol, directed, quant='all'):
    '''calculate the requested quantities for network'''
    common_qlist = ['Degree',
      'Connectivity',
      'AverageShortestPathLength',
      'BetweennessCentrality',
      'ClosenessCentrality',
      'ClusteringCoefficient',
      'Eccentricity',
      'NeighborhoodConnectivity',
      'SelfLoops',
      'Stress']
    dironly_qlist = ['Indegree', 'Outdegree']
    undironly_qlist = ['Radiality', 'TopologicalCoefficient']
    edgeqlist = ['EdgeBetweenness']
    notimplemented = []
    edgelist = list(zip(list(edgetab[sourcecol]), list(edgetab[targetcol])))
    ismulti = len(edgelist) > len(set(edgelist))
    
    if directed:
        G = nx.MultiDiGraph() if ismulti else nx.DiGraph()
    else:
        G = nx.MultiGraph() if ismulti else nx.Graph()
    #print('graph interpreted as', type(G))
    
    G.add_nodes_from(list(nodetab[idcol]))
    G.add_edges_from(edgelist)
    
    if quant == 'all':
        quantities = common_qlist+edgeqlist+(dironly_qlist if directed else undironly_qlist)
        quantities = [q for q in quantities if q not in notimplemented]
    elif type(quant) == str:
        quantities = [quant]
    elif type(quant) == list: 
        quantities = quant
    else:
        raise ValueError('quantity for network analysis must be string or list')
    
    # check validity of quantity names
    validq = common_qlist+dironly_qlist+undironly_qlist+edgeqlist
    kwcheck(quantities, validq, name='quantity|quantities', context=' in networkanalysis')
    
    nodeqdic = OrderedDict()
    edgeqdic = OrderedDict()
    for q in quantities:
        if q in notimplemented:
            raise ValueError('Not yet implemented: '+q)
        if directed and q in undironly_qlist:
            raise ValueError('Quantity not available for directed network: '+q)
        if not directed and q in dironly_qlist:
            raise ValueError('Quantity not available for undirected network: '+q)
        func = eval(q)
        if q in edgeqlist:
            dic = func(G) # dictionary with edges as keys
            # edge (u, v) may appear as (v, u) for undirected graphs, deal with it
            edgeqdic[q] = [dic[e] if e in dic else dic[e[::-1]] for e in zip(edgetab[sourcecol], 
              edgetab[targetcol])]
        else:
            dic = func(G) # dictionary with nodes as keys
            nodeqdic[q] = [dic[v] for v in nodetab[idcol]]
    return (nodeqdic, edgeqdic)
