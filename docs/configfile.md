---
title: Tabnetviz configuration options
---

#### [Home](index.md) | [User Guide](userguide.md) | [Tutorial](tutorial.md) | **Config file reference** | [Demo](demo.md) | [Gallery](gallery.md)

## tabnetviz yaml configuration file documentation
* **networktype:** `directed`|**`undirected`**\
  Type of network; optional.
* **title:** **_title_**\
  A title for the network; optional. For svg output, the title will be shown when the cursor hovers over the background. Default: "network". If you want to display a title for the graph, use the **label** attribute under the **graphattrs** keyword.
* **edgetable:**\
  Edge table specification; mandatory unless the edge table file name is specified on the command line (`-e` option). If you only provide a file name and don't use any of the other parameters below, you can use `edgetable:` **_filename_**.
    * **file:** **_filename_**\
      File name; mandatory. Can be overridden on the command line using the `-e` option.
    * **filetype:** `csv`|`tsv`|`xlsx`|`xls`\
      File type; optional; otherwise inferred from the file name.
    * **sheet:** **_sheetname_**\
      Worksheet name; optional; for xlsx/xls files only; otherwise the first sheet is taken.
    * **noheader:** `true`|**`false`**\
      Flag to indicate if the table has no header line; optional; must be set to true if the file has no column headers; in this case, columns will be named `col1`, `col2`,...
    * **sourcecolumn:** **_columnname_**\
      Name of column containing the source nodes of edges; optional. If not provided or there is no header then the first column will be used.
    * **targetcolumn:** _**columnname**_\
      Name of column containing the target nodes of edges; optional. If not provided or there is no header then the second column will be used.
    * **fromcytoscape:** **`no`** | `yes`\
      Indicates whether the edge table has been exported from Cytoscape.  Edge tables exported from Cytoscape do not contain separate source and target columns; the program will identify and separate them. The new columns will be named `source` and `target`.
* **nodetable:**\
  Node table specification; optional; if not provided then nodes will be inferred from the edge table. If you only provide a filename and don't use any of the other parameters below, you can use `nodetable:` **_filename_**.
    * **file:** **_filename_**\
      File name; mandatory. Can be overridden on the command line using the `-n` option.
    * **filetype:** `csv`|`tsv`|`xlsx`|`xls`\
      File type; optional; otherwise inferred from the file name.
    * **sheet:** **_sheetname_**\
      Worksheet name; optional; for xlsx/xls files only; otherwise the first sheet is taken.
    * **noheader:** `true`|**`false`**\
      Flag to indicate if the table has no header line; optional; must be set to true if the file has no column headers; in this case, columns will be named `col1`, `col2`,...
    * **idcolumn:** _**columnname**_\
      Name of column containing the node identifiers; optional. If not provided or there is no header then the first column will be used.
    * **skipisolated**: `true`|**`false`**\
      Skip nodes with no edges (i.e. zero-degree nodes). If true, these nodes will not be loaded at all. Useful if you have a large node table but only a small network. Optional.
* **outputfiles:**\
  Optional; names of output files. A drawing will always be saved; optionally a dot file, the modified node and edge tables, and an svg file containing colorbars can be saved. If you only specify a drawing file, you can use the short form: `outputfiles:` **_filename_**.
    * **drawing:** _**filename**_\
      Name of output drawing file; optional; if not provided then `out.svg` will be used. Extension will determine file type. SVG is the generally recommended format, but many image formats are also available. See the [Graphviz documentation](https://graphviz.gitlab.io/_pages/doc/info/output.html) for a list of available formats. Can be overridden on the command line using the `-o` option.
    * **dot:** **_filename_**\
      Name of dot output file; optional (not saved by default). The output dot file will contain node coordinates after layout; this can be loaded in a later run to produce another drawing with the same layout.
    * **nodetableout:** _filename_\
      Save the modified node table, i.e. after new columns from network analysis, rankings, Boolean columns defining node groups, and calculated non-Graphviz attributes have been added. The format can be csv, tsv, xlsx, or xls; the program will use the filename extension to decide the format. Optional; by default no file will be saved. Cannot be the same as the original node table file name. Can be overridden on the command line using the `--nodetableout` option.
    * **edgetableout:** _filename_\
      Save the modified edge table, i.e. after new columns from network analysis, rankings,  Boolean columns defining edge groups, and calculated non-Graphviz attributes have been added. The format can be csv, tsv, xlsx, or xls; the program will use the filename extension to decide the format. Optional; by default no file will be saved. Cannot be the same as the original edge table file name. Can be overridden on the command line using the `--edgetableout` option.
    * **colorbars:** _filename_\
      Save an SVG file named _filename_ containing color bars for the colormaps used in the node style and edge style mappings. These can then be used to create a legend for your visualization. Optional; if not specified then no such file will be created.
* **layout:** **`neato`**|`dot`|`twopi`|`circo`|`fdp`|`sfdp`|`patchwork`|`osage`| **_dotfilename_**\
  Specify a layout algorithm or a dot file to take a pre-generated layout from. If a dot file is specified, it must contain the same network as the current network, and must contain position coordinates for all nodes and edges.
* **graphattrs:**\
  Optional additional Graphviz graph attributes. By default, `outputorder: edgesfirst`,  and `overlap: false`, will be set for nicer visual appearance of the graph.
    * **_graphattrname_: _graphattrvalue_**\
      Graph attribute name and value, see Graphviz documentation.
    * **_graphattrname_: _graphattrvalue_**\
      An arbitrary number of further graph attributes can be specified.  
* **remove:**\
  Remove some nodes and edges before laying out the network (optional). This will be done before the network analysis, if any.
    * **nodes:** _columnexpression_\
      A Boolean expression defining the set of nodes to remove. The expression can use node table column names and simple numerical or string operations on them. Examples: `Age < 10`, `Country == 'Germany'`.
    * **edges:** _columnexpression_\
      A Boolean expression defining the set of edges to remove. The expression should use edge table column names.
    * **keepisolatednodes:** **`false`** | `true`\
      Indicates whether nodes becoming isolated (degree=0) after the removal of edges should be kept. The default is false, i.e. they will be deleted. Note that nodes that were already isolated before the edge removal will not be removed.
* **networkanalysis:** **`false`** | `all` | **_quantity_** | **[_quantity1, quantity2, ..._]**\
  Indicate whether a network analysis should be performed (`false` by default). Graph theoretical quantity names can be provided, either a single quantity, a list of quantities, or the keyword `all` to calculate all quantities. The calculated quantities will be added as new columns to the node table and the edge table, and can then be used to specify node styles and edge styles. The following quantities can be calculated for each node for both directed and undirected networks: **AverageShortestPathLength, BetweennessCentrality, ClosenessCentrality, ClusteringCoefficient, Degree, Connectivity, Eccentricity,  NeighborhoodConnectivity, SelfLoops, Stress**. For edges, **EdgeBetweenness** can be calculated. For directed networks only, **Indegree** and **Outdegree** can be calculated. For undirected networks only, **Radiality** and **TopologicalCoefficient** can be calculated. These quantity names match those calculated by the Network Analyzer plugin of Cytoscape, except for **Connectivity**, which is the number of neighbors of a node, as opposed to **Degree** which is the number of edges connecting to a node.
* **nodegroups:**\
  Groups of nodes can be defined; optional.
    * _**groupname: columnexpression**_ | **[_node1, node2, ..._]**\
      Node group name and a Boolean expression to define the node group, or an explicit node list. The expression can use node table column names and simple numerical or string operations on them. Examples: `mynodegroup1: a+b < 5`, `mynodegroup2: firstname.str.upper() < 'M'`. Nodes can also be explicitly listed by name, e.g. `[node1, node13', node128]`.
    * _**groupname: columnexpression**_ | **[_node1, node2, ..._]**\
      An arbitrary number of further node groups can be defined. When a group is defined, it is added to the node table as a Boolean column so it can be used in the definition of subsequent groups. For this reason, node group names cannot be identical to existing node table column names.
* **edgegroups:**\
  Groups of edges can be defined; optional.
    * _**groupname: columnexpression**_ | **[(_source1, target1_), (_source2, target2_), ...]**\
      Edge group name and a Boolean expression to define the edge group, or an explicit edge list. The expression can use edge table column names and simple numerical or string operations on them. Examples: `myedgegroup1: abs(c) > 3`, `myedgegroup2: interaction.str.lower() >= 'p'`.  Edges can also be explicitly listed by listing **(_source, target_)** pairs, e.g. `[(node1, node23), (node45, node57)]`
    * _**groupname: columnexpression**_ | **[(_source1, target1_), (_source2, target2_), ...]**\
      An arbitrary number of further edge groups can be defined. When a group is defined, it is added to the edge table as a Boolean column so it can be used in the definition of subsequent groups. For this reason, edge group names cannot be identical to existing edge table column names.
* **clusters:** **_nodegroup1_** | **[_nodegroup1, nodegroup2, ..._]**\
  Define clusters as node groups (simple form without style specifications). Node groups should be listed in brackets (which can be omitted if there is only one cluster). The **dot** and **fdp** layout algorithms will draw a box around the nodes belonging to a cluster. Only node groups defined above under the **nodegroups** keyword can be used. If you simply list the node groups corresponding to clusters, they will be drawn with the default cluster styles. Otherwise, you can specify styles for each cluster, see below.
* **clusters:**\
  Define clusters as node groups, specifying styles for each cluster. Only node groups defined above under the nodegroups keyword can be used.
    * **_nodegroup1_:**\
      Specify Graphviz cluster attribute name-value pairs below. These will be used for the cluster corresponding to this node group.
        * **_attributename: attributevalue_**\
          A Graphviz cluster attribute name and its value. See available cluster attributes (indicated by the letter C) in the [Graphviz documentation](https://www.graphviz.org/doc/info/attrs.html).  Commonly used cluster attributes include `color`, `fillcolor`, `label`, `labelloc`, `fontname`, `fontsize`, `fontcolor`, `style` (= `solid`, `dashed`, `dotted`, `rounded`, `filled`, etc.)
        * **_attributename: attributevalue_**\
          Any number of further attribute names and values can be provided.
        * ...
    * **_nodegroup2:_**\
      Cluster attributes for another node group, if any.
        * **_attributename: attributevalue_**\
          As above.
        * ...
    * **_nodegroup3_:**\
      If you don't want to provide cluster attributes, it's enough to provide the node group name, but make sure you place a colon (`:`) after it.
* **clusters:**\
  Alternative form of defining clusters: provide a list instead of a dictionary. Use the dash (`-`) in front of node group names. 
    * **- _nodegroup1_:**
        * **_attributename: attributevalue_**\
          See above
        * ...
    * **- _nodegroup2:_**
        * **_attributename: attributevalue_**
        * ...
    * **_- nodegroup3_**\
      If you don't want to provide cluster attributes, it's enough to provide the node group name (note the dash `-` is needed but no colon `:` must be used).
* **addrankings:**\
  Add table columns containing rankings of values in existing columns; optional. These new columns can then be used for visual style definitions.
    * **_columnname_:**\
      Name of new column that will contain the ranking.
        * **table:** `nodetable`|`edgetable`\
          Whether the ranking will be in the node table or the edge table; mandatory.
        * **colexpr:** **_columnname_ | _columnexpression_**\
          Name of column or an expression with column names; these values will be ranked.
        * **method:** **`average`** | `min` | `max` | `first` | `dense`\
          How to treat groups of equal values: take the average rank, min/max rank, or appearance order (`first`). `dense` is like `min` but increases the rank by 1 between groups. Optional.
        * **reverse:** **`false`**|`true`\
          Whether to reverse the ranking; optional.
        * **withingroup:** _**groupname**_\
          Provide node/edge group name if the ranking is to be performed within that group only.
    * **_columnname_:**\
      An arbitrary number of further rankings can be defined.
* **colormaps:**\
  Custom color maps can be defined, in addition to the standard **matplotlib** colormaps.
    * **_colormapname_:**\
      A name for the color map.
        * **type:** `discrete`|`continuous`\
          Indicates whether we want a fixed number of colors or a smoothly changing scale.
        * **map:**\
          The mapping; a list of colors for `type: discrete`.
            * **- _color_**\
              Any Graphviz color specification can be used.
            * **- _color_**
            * **- _color_**\
              Any number of additional colors can be defined.
        * **map:**\
          The mapping; a number of **_value: color_** pairs for `type: continuous`; the values must be floating point values between 0.0 and 1.0; the first value must be 0.0 and the last must be 1.0
            * `0.0`**:** **_color_**\
              CSS4 color names and hexadecimal RGB and RGBA colors can be used. Examples: `turquoise`, `'#FAEBD7'`, `'#FAEBD7CC'`. Note: hexadecimal colors must be enclosed in single or double quotes, otherwise they will be interpreted as comments due to the `#` character.
            * **_value_:** **_color_**
            * ...
            * `1.0`**:** **_color_**
    * **_colormapname_:**\
      Any number of custom color maps can be defined.
        * ...
* **nodestyles:**\
  Define node styles for all nodes and/or node groups using various types of mappings of data from the node table. This is the main functionality of the program.
    * **default** | **_nodegroupname_:**\
      The style can be for all nodes (**default**) or a particular node group.
        * **_attributename_:** _**constant**_\
          Specify a constant value for the given Graphviz attribute.
        * **_attributename_:**\
          A node attribute name; will be used in a mapping. Any Graphviz node attribute name can be used. Non-Graphviz, user-defined attribute names can be also used, these can then be combined into a multi-valued Graphviz attribute (e.g. **pos**, or a color specified by a **colorList**) using the `combine` mapping type. **NOTE:** Non-Graphviz attribute names must start with the prefix `ng` to make sure there is no Graphviz attribute with the same name. See [Graphviz attribute definitions](www.graphviz.org/doc/info/attrs.html). Non-Graphviz attributes will be added as new columns to the node table, and can also be used to define further attributes.
            * **type:** `direct`|`discrete`|`linear`|`cont2disc`|`colormap`|`combine`\
              Type of mapping to be used to map values in the node table to visual attributes.
            * _(the rest of the parameters depend on **type**; see details below)_
        * **_attributename_:**\
          For direct mapping of table data to attribute.
            * **type:** `direct`\
              Attribute value will be taken directly from the node table; either a single column, or calculated from an expression on column values.
            * **colexpr:** **_columnname_** | **_columnexpression_**\
              Name of a single column, or a numerical or string expression formed from column names. Examples: `colexpr: a`, `colexpr: abs(a)+b/c`, `colexpr: a.str.upper()+b`
        * **_attributename_:**\
          For discrete mapping.
            * **type:** `discrete`\
              Discrete values in table will be mapped to the values provided here.
            * **colexpr:** **_columnname_** | **_columnexpression_**\
              Name of a single column, or a numerical or string expression formed from column names. Examples: `colexpr: a`, `colexpr: abs(a)+b/c`, `colexpr: a.str.upper()+b`
            * **map:**\
              Map is specified below
                * **_value_:** **_mappedvalue_**\
                  Value in table and value to map it to.
                * **_value_:** **_mappedvalue_** ...\
                  Any number of further values and mapped values can be specified.
        * **_attributename_:**\
          For linear mapping.
            * **type:** `linear`\
              Values in column, or calculated from an expression on columns, will be linearly mapped to a given interval.
            * **colexpr:** **_columnname_** | **_columnexpression_**\
              Name of a single column, or a numerical expression formed from column names. Examples: `colexpr: a`, `colexpr: abs(a)+b/c`
            * **colmin:** _**value**_\
              Optional; minimum value to map; if not provided then the calculated minimum will be used.
            * **colmax:** _**value**_\
              Optional; maximum value to map; if not provided then the calculated maximum will be used.
            * **mapmin:** **_value_**\
              Mandatory; **colmin** will be mapped to this value.
            * **mapmax:** **_value_**\
              Mandatory; **colmax** will be mapped to this value; it can be less than **mapmin**.
            * **withingroup:** **`false`**|`true`\
              Optional; if set to true then **colmin** and **colmax** will be calculated for the given node group (if they are not explicitly specified).
        * **_attributename_:**\
          For continuous-to-discrete mapping.
            * **type:** `cont2disc`\
              Map ranges to discrete values.
            * **colexpr:** **_columnname_** | **_columnexpression_**\
              Name of a single column, or a numerical or string expression formed from column names. Examples: `colexpr: a`, `colexpr: abs(a)+b/c`, `colexpr: a.str.upper()+b`
            * **map:**\
              Define the mapping.
                * **_value1_:** _**mappedvalue1**_\
                  _x_ <= **_value1_** will be mapped to **_mappedvalue1_**
                * **_value2_:** _**mappedvalue2**_\
                  **_value1_** < _x_ <= **_value2_** will be mapped to **_mappedvalue2_**
                * ...\
                  Further specifications...
                * **_valueN_:** _**mappedvalueN**_\
                  **_value(N-1)_** < _x_ <= **_valueN_** will be mapped to **_mappedvalueN_**
                * **higher:** **_mappedvaluehigh_**\
                  _x_ > **_valueN_** will be mapped to **_mappedvaluehigh_**
        * **_attributename_:**\
          For mapping to a color scale or discrete colormap.
            * **type:** `colormap`\
              Map numerical column to a continuous color scale or a set of discrete colors. Usually, one uses a discrete colormap for integer values and a continuous colormap for floating point values.
            * **colexpr:** **_columnname_** | **_columnexpression_**\
              Name of a single column, or a numerical expression formed from column names. Examples: `colexpr: a`, `colexpr: abs(a)+b/c`
            * **colmin:** _**value**_\
              Optional; minimum value to map; if not provided then the calculated minimum will be used.
            * **colmax:** _**value**_\
              Optional; maximum value to map; if not provided then the calculated maximum will be used.
            * **centerzero:** **`no`**|`aligncloser`|`alignfarther`|`piecewise`\
              If not `no` then map the zero value to the center of the colormap. The keyword determines how the colmin/colmax values will be mapped to the ends of the colormap. `aligncloser` aligns the value closer to zero to one end of the colormap; `aligncloser` maps the value farther from zero to one end of the colormap; `piecewise` will align both colmin and colmax to the ends of the colormap by using different scaling below and above zero. If the range of the data does not include zero then this parameter must be `no` (default).
            * **colormap:** **_colormapname_**\
              Name of a colormap; colormaps known to **matplotlib** and custom color maps defined in **colormaps** can be used.
            * **reverse:** **`no`**|`yes`\
              If `yes`, reverse the color scale. Note that most matplotlib colormaps can be reversed by appending `_r` to the name, e.g. the reverse of `bwr` is `bwr_r`.
            * **withingroup:** **`false`**|`true`\
              Optional; if set to true then **colmin** and **colmax** will be calculated for the given node group (if they are not explicitly specified).
        * **_attributename_:**\
          For the `combine` mapping type; a Graphviz attribute that uses multiple values, e.g. **pos** (which uses x and y coordinates), or a color using a **colorList**, etc.
            * **type:** `combine`\
              Combine previously defined non-Graphviz attributes into a multi-value Graphviz attribute. For example, if you previously defined mappings for **x** and **y** coordinates, you can now combine them into the **pos** Graphviz attribute. The combining is done by formatting a tuple of the attributes using a format string.
            * **attrlist:**\
              List of previously defined non-Graphviz attributes to combine. Can also be provided on a single line using brackets, e.g. `[x, y]` (i.e. a valid YAML list).
                * **- _attributename1_**
                * **- _attributename2_**
                * ...\
                  Any number of attributes can be listed
            * **formatstring:** **'_formatstring_'**\
              An old-style Python format string (using `%` -style specifiers) with which the attribute list will be converted into a string. Examples: `'%f,%f!'` (for **pos**), `'#%02x%02x%02x'` (an RGB color from 3 integers), `'%s:%s:%s'` (a colorList from 3 strings). The format string must be enclosed in quotes (single or double) if it starts with the `%` character.
    * ...\
      Styles can be defined for any number of further node groups.
* **edgestyles:**\
  Define edge styles for all edges and/or edge groups.
    * **default:** | **_edgegroupname_:**\
      The style can be for all edges (**default**) or a particular edge group.
        * ...\
          See **nodestyles** for descriptions of various mappings and their parameters; syntax is identical but edge table is used instead of node table, and edge groups instead of node groups.
          
