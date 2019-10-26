'''tabnetviz configuration file template module'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html

template = """#
# CONFIGURATION TEMPLATE FILE FOR TABNETVIZ
# Edit and (un)comment lines to prepare your own configuration file
# ----------
# Network type
networktype: directed      # directed | undirected
#
# Define edge table
#
#edgetable: edges.csv      # short form if you don't provide any other parameters
edgetable:
  filetype: xlsx           # csv|tsv|xlsx|xls (optional)
  file: edges.xlsx         # .csv, .tsv, .xlsx/.xls
  sheet: Sheet1            # only for .xlsx/.xls, first sheet is used if omitted
  noheader: false          # true if table has no header line (col1, col2,... will be used)
  sourcecolumn: source     # name of source column ("source" by default)
  targetcolumn: target     # name of target column ("target" by default)
  fromcytoscape: no        # set to yes if exported from Cytoscape
#
# Define node table
#
#nodetable: nodes.csv      # short form if you don't provide any other parameters
nodetable:                 # optional; nodes will be inferred from edge table if omitted
  filetype: xlsx           # csv|tsv|xlsx|xls (optional)
  file: example.xlsx       # .csv, .tsv, .xlsx/.xls
  sheet: Sheet1            # only for .xlsx/.xls, first sheet is used if omitted
  noheader: false          # true if table has no header line (col1, col2, ... will be used)
  idcolumn: name           # name of node id column ("name" by default)
  skipisolated: false      # set to true to skip isolated nodes
#
# Output files
#
outputfiles:
  drawing: file.svg        # for the drawing
  dot: dotfile.dot         # for dot file containing positions after layout
#
# Define layout
#
layout: neato              # neato|dot|twopi|circle|fdp|sfdp|patchwork (see graphviz docs)
#
# Graph attributes (note: "outputorder: edgesfirst" and "overlap: false" are set by default)
#
graphattrs:
  attrname1: attrvalue1    # see Graphviz doc for available graph attributes
  attrname2: attrvalue2
#
# Perform network analysis
#
networkanalysis: false     # set to 'all' or list of quantity names, see documentation
#
# Define node groups
#
nodegroups:                # optional; define node groups using boolean queries
  group1: expr1            # node group name: boolean expression with node table column names
  group2: expr2          
#
# Define edge groups
#
edgegroups:                # optional; define edge groups using boolean queries
  group1: expr1            # edge group name: expression with edge table column names as query
  group2: expr2
#
# Define clusters (note: layout must be dot or fdp)
# (clusters are node groups with a box drawn around them)
#
clusters: group1
# alternative form:
clusters: [group1, group2]
# specifying clusters with visual attributes:
clusters:
  group1:                # a previously defined node group name
    attrname1: value1    # a Graphviz cluster attribute and its value
    attrname2: value2
  group2:                # another node group
    attrname: value
  group3:                 # this cluster will use default attributes (":" is necessary!)
# alternative form using a list:
clusters:
  - group1:                # a previously defined node group name
      attrname1: value1    # a Graphviz cluster attribute and its value
      attrname2: value2
  - group2:                # another node group
      attrname: value
  - group3                 # this cluster will use default attributes
# 
# Add table columns containing rankings of existing table columns
#
addrankings:               # optional; add columns containing rankings of existing columns
  rankcol1:                # new column name for the ranking
    table: nodetable       # nodetable|edgetable
    colexpr: colname1      # existing column name or expression
    method: average        # how to treat equal values: average|min|max|first|dense
    reverse: false         # true for reverse ranking
    withingroup: example1  # optional; rank only within the given group
  rankcol2:                # another ranking
    table: edgetable
    reverse: true
    withingroup: example2
#
# Define custom color maps
#
colormaps:
  colormapname1:           # a name for the new color map
    type: discrete         # discrete|continuous
    map:                   # actual map here
      - green              # can use color names
      - white
      - '#FAEBD7'          # RGB code
      - '#FAEBD7CC'        # RGBA code
  colormapname2:           # name for colormap
    type: continuous
    map:                   # continuous colormap example
      0.0: red             # must provide colors for values between 0.0 and 1.0
      0.5: white
      1.0: blue
#
# Define node styles
#
nodestyles:                # define node styles for node groups
  # define default node style
  default:                 # default style, means all nodes
    attribute0:            # a Graphviz node attribute name
      type: direct         # mapping type: direct|discrete|linear|cont2disc|colormap|combine
      colexpr: columnname1 # node table column name or expression
  #
  # styles for nodes in node group "group1"
  #
  group1:                  # a node group name
    attribute1: const1     # constant "mapping": a graphviz node attribute name: constant value
    attribute2:            # another attr
      type: direct         # direct mapping from a table column or column expression
      colexpr: col1+col2   # node table column name or expression on column names
    attribute3:            # another attr
      type: discrete       # discrete-to-discrete mapping
      colexpr: col1        # column name or expression
      map:                 # specify map
        value1: mapped1    # a value and its mapping
        value2: mapped2
    attribute4:            # another attr
      type: linear         # continuous-to-continuous linear mapping
      colexpr: col2        # column name or expression with column names to map
      colmin: value1       # minimum value to map (optional; default is actual minimum)
      colmax: value2       # maximum value to map (optional; default is actual maximum)
      mapmin:              # minimum value after mapping
      mapmax:              # maximum value after mapping
      withingroup: false   # if true, colmin and colmax will be calculated within group1
    attribute5:
      type: cont2disc      # continuous to discrete mapping
      colexpr: col3        # column name or expression
      map:
        value1: mapped1    # x <= value1 will be mapped to mapped1
        value2: mapped2    # value1 < x <= value2 will be mapped to mapped2
        valueN: mappedN
        higher: mappedH    # x > higher will be mapped to mappedH
    attribute6:
      type: colormap       # map values to colors
      colexpr: col4        # column name or expression on column names
      colmin: value1       # minimum value to map (optional; default is actual minimum)
      colmax: value2       # maximum value to map (optional; default is actual maximum)
      centerzero: no       # no|aligncloser|alignfarther|piecewise (see docs)
      colormap: colormapname1 # any Matplotlib colormap name, or name of custom colormap
      reverse: no          # yes to reverse
      withingroup: false   # if true, colmin and colmax will be calculated within group1
    ngattr1:               # non-Graphviz attribute, must be prefixed with "ng"
      type: direct         # can use any mapping, example here is "direct"
      colexpr: col1+4.0    # column name or expression on column names
    ngattr2:               # another non-Graphviz attribute
      type: direct         # can use any mapping, example here is "direct"
      colexpr: col2-5.0    # column name or expression on colum names
    attribute7:            # a Graphviz attribute
      type: combine        # combine previously defined attributes
      attrlist:            # list of attributes to combine
        - ngattr1
        - ngattr2          # can also use "attrlist: [ngattr1, ngattr2]"
      formatstring: '%f,%f!' # old-style Python format string to combine attributes
  #
  # styles for nodes in node group "group2"
  group2:                  # a node group name
    attribute:             # a graphviz node attribute name
    # ... continue as for group1
#
# Define edge styles
# All syntax is the same as for nodestyles, but groups are meant to be edge groups
#
edgestyles:                # define edge styles for edge groups
  default:                 # optional; default style
    attribute:             # a graphviz edge attribute name
    # ... continue as with nodestyles
  group1:                  # an edge group name
    attribute:             # a graphviz edge attribute name
    # ... continue as with nodestyles
  group2:                  # an edge group name           
    attribute:             # a graphviz edge attribute name
    # ... continue as with nodestyles
"""
