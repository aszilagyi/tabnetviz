#!/usr/bin/env python3

'''output colorbars used in tabnetviz config file as svg file'''

# Copyright 2019 Andras Szilagyi
# Distributed under the GNU General Public License v3
# See https://www.gnu.org/licenses/gpl-3.0.html

import svgwrite
from matplotlib import cm, colors

def valconv(x):
    tname = type(x).__name__
    if 'str' in tname:
        return x
    if 'int' in tname:
        return '%d' % (x)
    if 'float' in tname:
        return '%g' % (x)
    return str(x)

class ColorBars():
    def __init__(self):
        self.colorbarlist = []
    def add(self, cmap, minval=0.0, maxval=1.0, title='Colorbar',
      left=0.0, center=0.5, right=1.0, reverse=False):
        self.colorbarlist.append((cmap, minval, maxval, title, left, center, right, reverse))
    def writesvg(self, fname):
        ncb = len(self.colorbarlist)
        if ncb == 0:
            return
        # create svg drawing
        dwg = svgwrite.Drawing(fname, size=(900, (ncb+1)*100-50))
        # create linear gradients
        j = 0
        for (cmap, minval, maxval, title, left, center, right, reverse) in self.colorbarlist:
            if type(cmap) == colors.LinearSegmentedColormap:
                j += 1
                sd = cmap._segmentdata
                # x values
                xvals = sorted(set(row[0] for e in sd for row in sd[e])|{0.0, 0.5, 1.0})
                lg = dwg.linearGradient(id='c'+str(j))
                # transform xvals if necessary
                fL = (center-left)/0.5
                fR = (right-center)/0.5
                xxvals = [left+fL*x if x < 0.5 else center+fR*(x-0.5) for x in xvals]
                xxvals = [x for x in xxvals if 0.0 <= x <= 1.0]
                xxvals = sorted(set(xxvals)|{0.0, center, 1.0})
                # map these values back
                bxvals = [(x-left)/fL if x < center else 0.5+(x-center)/fR for x in xxvals]
                if reverse:
                    xxvals = [1.0-x for x in xxvals]
                    xxvals.reverse()
                    bxvals.reverse()
                for (xval, bxval) in zip(xxvals, bxvals):
                    col = cmap(bxval)
                    hexcol = colors.to_hex(col, keep_alpha=False)
                    opac = col[3]
                    lg.add_stop_color(offset=xval, color=hexcol, opacity=opac)
                dwg.defs.add(lg)
        # draw colorbars and text
        j = 0
        i = 0
        for (cmap, minval, maxval, title, left, center, right, reverse) in self.colorbarlist:
            i += 1
            y = 100*i-50
            # set title
            ttext = dwg.text(title, insert=(450, y-10), fill='black', font_size='30px', 
              text_anchor='middle', font_family='sans-serif')
            dwg.add(ttext)
            # set min and max vals
            tmin = valconv(minval)
            tmax = valconv(maxval)
            ttmin = dwg.text(tmin, insert=(290, y+37), fill='black', font_size='24px',
              text_anchor='end', font_family='sans-serif')
            dwg.add(ttmin)
            ttmax = dwg.text(tmax, insert=(610, y+37), fill='black', font_size='24px',
              text_anchor='start', font_family='sans-serif')
            dwg.add(ttmax)
            if type(cmap) == colors.LinearSegmentedColormap:
                j += 1
                box = dwg.rect(insert=(300, y), size=(300, 50), fill='url(#c'+str(j)+')')
                dwg.add(box)
            elif type(cmap) == colors.ListedColormap:
                n = len(cmap.colors)
                hexcols = [colors.to_hex(c) for c in cmap.colors]
                if reverse:
                    hexcols.reverse()
                b = 300/n
                for k in range(n):
                    box = dwg.rect(insert=(300+k*b, y), size=(b, 50), fill=hexcols[k])
                    dwg.add(box)
        dwg.save()
        

# main section (for testing only)

if __name__ == '__main__':
    
    cbs = ColorBars()
    cmap = cm.get_cmap('bwr')
    cbs.add(cmap, minval=-3.145, maxval=5.879, title='bwr')
    cbs.add(cmap, minval=-3.145, maxval=5.879, title='bwr_r', reverse=True)
    cbs.add(cmap, minval=-3.145, maxval=5.879, left=-0.5, center=0.4, right=1.5, title='bwrshift')
    cmap = colors.ListedColormap(['green', 'yellow', 'pink', 'gray'])
    cbs.add(cmap, minval=31, maxval=34, title='listed')
    cbs.add(cmap, minval=31, maxval=34, title='listed_r', reverse=True)
    cmap = colors.LinearSegmentedColormap.from_list('mymap', [(0.0, 'red'), (0.2, 'green'), 
    (0.3, 'yellow'), (0.6, 'white'), (1.0, 'orange')])
    cbs.add(cmap, title='5 colors')
    cbs.add(cmap, title='5 colors rev', reverse=True)
    cbs.add(cmap, title='5 colors transformed', left=0.6, center=0.7)
    cbs.add(cmap, title='5 colors transformed rev', left=0.6, center=0.7, reverse=True)
    cbs.writesvg('colorbarsvg_test.svg')
    
