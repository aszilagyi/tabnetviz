#!/usr/bin/env python3

'''Graphviz attribute list'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html
# Attribute list is from the Graphviz web site at https://www.graphviz.org/doc/info/attrs.html

txt = '''Name	Used By	Type	Default	Minimum	Notes	
Damping	G	double	0.99	0.0	neato only	
K	GC	double	0.3	0	sfdp, fdp only	
URL	ENGC	escString	<none>		svg, postscript, map only	
_background	G	string	<none>			
area	NC	double	1.0	>0	patchwork only	
arrowhead	E	arrowType	normal			
arrowsize	E	double	1.0	0.0		
arrowtail	E	arrowType	normal			
bb	G	rect			write only	
bgcolor	GC	color colorList	<none>			
center	G	bool	false			
charset	G	string	"UTF-8"			
clusterrank	G	clusterMode	local		dot only	
color	ENC	color colorList	black			
colorscheme	ENCG	string	""			
comment	ENG	string	""			
compound	G	bool	false		dot only	
concentrate	G	bool	false			
constraint	E	bool	true		dot only	
decorate	E	bool	false			
defaultdist	G	double	1+(avg. len)*sqrt(|V|)	epsilon	neato only	
dim	G	int	2	2	sfdp, fdp, neato only	
dimen	G	int	2	2	sfdp, fdp, neato only	
dir	E	dirType	forward(directed)none(undirected)			
diredgeconstraints	G	string bool	false		neato only	
distortion	N	double	0.0	-100.0		
dpi	G	double	96.00.0		svg, bitmap output only	
edgeURL	E	escString	""		svg, map only	
edgehref	E	escString	""		svg, map only	
edgetarget	E	escString	<none>		svg, map only	
edgetooltip	E	escString	""		svg, cmap only	
epsilon	G	double	.0001 * # nodes(mode == KK).0001(mode == major)		neato only	
esep	G	addDouble addPoint	+3		not dot	
fillcolor	NEC	color colorList	lightgrey(nodes)black(clusters)			
fixedsize	N	boolstring	false			
fontcolor	ENGC	color	black			
fontname	ENGC	string	"Times-Roman"			
fontnames	G	string	""		svg only	
fontpath	G	string	system-dependent			
fontsize	ENGC	double	14.0	1.0		
forcelabels	G	bool	true			
gradientangle	NCG	int	""			
group	N	string	""		dot only	
headURL	E	escString	""		svg, map only	
head_lp	E	point			write only	
headclip	E	bool	true			
headhref	E	escString	""		svg, map only	
headlabel	E	lblString	""			
headport	E	portPos	center			
headtarget	E	escString	<none>		svg, map only	
headtooltip	E	escString	""		svg, cmap only	
height	N	double	0.5	0.02		
href	GCNE	escString	""		svg, postscript, map only	
id	GCNE	escString	""		svg, postscript, map only	
image	N	string	""			
imagepath	G	string	""			
imagepos	N	string	"mc"			
imagescale	N	boolstring	false			
inputscale	G	double	<none>		fdp, neato only	
label	ENGC	lblString	"\\N" (nodes)"" (otherwise)			
labelURL	E	escString	""		svg, map only	
label_scheme	G	int	0	0	sfdp only	
labelangle	E	double	-25.0	-180.0		
labeldistance	E	double	1.0	0.0		
labelfloat	E	bool	false			
labelfontcolor	E	color	black			
labelfontname	E	string	"Times-Roman"			
labelfontsize	E	double	14.0	1.0		
labelhref	E	escString	""		svg, map only	
labeljust	GC	string	"c"			
labelloc	NGC	string	"t"(clusters)"b"(root graphs)"c"(nodes)			
labeltarget	E	escString	<none>		svg, map only	
labeltooltip	E	escString	""		svg, cmap only	
landscape	G	bool	false			
layer	ENC	layerRange	""			
layerlistsep	G	string	","			
layers	G	layerList	""			
layerselect	G	layerRange	""			
layersep	G	string	" :\t"			
layout	G	string	""			
len	E	double	1.0(neato)0.3(fdp)		fdp, neato only	
levels	G	int	MAXINT	0.0	sfdp only	
levelsgap	G	double	0.0		neato only	
lhead	E	string	""		dot only	
lheight	GC	double			write only	
lp	EGC	point			write only	
ltail	E	string	""		dot only	
lwidth	GC	double			write only	
margin	NCG	double point	<device-dependent>			
maxiter	G	int	100 * # nodes(mode == KK)200(mode == major)600(fdp)		fdp, neato only	
mclimit	G	double	1.0		dot only	
mindist	G	double	1.0	0.0	circo only	
minlen	E	int	1	0	dot only	
mode	G	string	major		neato only	
model	G	string	shortpath		neato only	
mosek	G	bool	false		neato only	
newrank	G	bool	false		dot only	
nodesep	G	double	0.25	0.02		
nojustify	GCNE	bool	false			
normalize	G	double bool	false		not dot	
notranslate	G	bool	false		neato only	
nslimit	G	double			dot only	
nslimit	G	double			dot only	
ordering	GN	string	""		dot only	
orientation	N	double	0.0	360.0		
orientation	G	string	""			
outputorder	G	outputMode	breadthfirst			
overlap	G	string bool	true		not dot	
overlap_scaling	G	double	-4	-1.0e10	prism only	
overlap_shrink	G	bool	true		prism only	
pack	G	boolint	false			
packmode	G	packMode	node			
pad	G	double point	0.0555 (4 points)			
page	G	double point				
pagedir	G	pagedir	BL			
pencolor	C	color	black			
penwidth	CNE	double	1.0	0.0		
peripheries	NC	int	shape default(nodes)1(clusters)	0		
pin	N	bool	false		fdp, neato only	
pos	EN	point splineType				
quadtree	G	quadType bool	normal		sfdp only	
quantum	G	double	0.0	0.0		
rank	S	rankType			dot only	
rankdir	G	rankdir	TB		dot only	
ranksep	G	double doubleList	0.5(dot)1.0(twopi)	0.02	twopi, dot only	
ratio	G	doublestring				
rects	N	rect			write only	
regular	N	bool	false			
remincross	G	bool	true		dot only	
repulsiveforce	G	double	1.0	0.0	sfdp only	
resolution	G	double	96.00.0		svg, bitmap output only	
root	GN	string bool	<none>(graphs)false(nodes)		circo, twopi only	
rotate	G	int	0			
rotation	G	double	0		sfdp only	
samehead	E	string	""		dot only	
sametail	E	string	""		dot only	
samplepoints	N	int	8(output)20(overlap and image maps)			
scale	G	double point			not dot	
searchsize	G	int	30		dot only	
sep	G	addDouble addPoint	+4		not dot	
shape	N	shape	ellipse			
shapefile	N	string	""			
showboxes	ENG	int	0	0	dot only	
sides	N	int	4	0		
size	G	double point				
skew	N	double	0.0	-100.0		
smoothing	G	smoothType	"none"		sfdp only	
sortv	GCN	int	0	0		
splines	G	boolstring				
start	G	startType	""		fdp, neato only	
style	ENCG	style	""			
stylesheet	G	string	""		svg only	
tailURL	E	escString	""		svg, map only	
tail_lp	E	point			write only	
tailclip	E	bool	true			
tailhref	E	escString	""		svg, map only	
taillabel	E	lblString	""			
tailport	E	portPos	center			
tailtarget	E	escString	<none>		svg, map only	
tailtooltip	E	escString	""		svg, cmap only	
target	ENGC	escStringstring	<none>		svg, map only	
tooltip	NEC	escString	""		svg, cmap only	
truecolor	G	bool			bitmap output only	
vertices	N	pointList			write only	
viewport	G	viewPort	""			
voro_margin	G	double	0.05	0.0	not dot	
weight	E	intdouble	1	0(dot,twopi)1(neato,fdp)		
width	N	double	0.75	0.01		
xdotversion	G	string			xdot only	
xlabel	EN	lblString	""			
xlp	NE	point			write only	
z	N	double	0.0	-MAXFLOAT-1000		
'''

gvattrs = {'G':set(), 'E':set(), 'N':set(), 'C':set(), 'S':set()}
for line in txt.splitlines()[1:]:
    v = line.split('\t')
    for c in v[1]:
        gvattrs[c].add(v[0])

if __name__ == '__main__':
    for T in 'SC':
        print(T, 'attributes:')
        for a in sorted(gvattrs[T]):
            print('  ', a)
