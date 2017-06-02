from PIL import Image
from sklearn.cluster import KMeans
import numpy as np
import os, os.path
import sys
from random import choice
import progressbar

if len(sys.argv) < 2:
    sys.exit('Input folder is not specified')
rootdir = sys.argv[1]

if len(sys.argv) < 3:
    no_clusters = 5;
else:
    no_clusters = int(sys.argv[2])

if len(sys.argv) < 4:
    saveToFile = False
else:
    saveToFile = True

# initialisation
filelist = []
hist = []
totalfile = len([name for name in os.listdir(rootdir) if os.path.isfile(os.path.join(rootdir,name))])

bar = progressbar.ProgressBar(maxval=totalfile, widgets=[progressbar.Bar('=','[',']'), ' ', progressbar.Percentage()])

print 'Analysing images ...'

bar.start()
i = 0
# read file and create histograms
for subdir,dirs,files in os.walk(rootdir):
   for f in files:
       filename = os.path.join(subdir,f)
       filelist.append(filename)

       img = Image.open(filename)

       h = img.histogram()

       hist.append(np.array(h))

       i = i+1
       bar.update(i)
bar.finish()

print 'Performing machine learning magic'
# KMeans clustering
hist = np.stack(hist)

kmeans = KMeans(n_clusters=no_clusters).fit(hist)

labels = kmeans.labels_

print 'Delivering your images...'
# puting each file into its own cluster
memberlist = []
for i in range(0,no_clusters):
    memberlist.append(list())

for i in range(0,len(filelist)):
    memberlist[labels[i]].append(filelist[i])

# display an example of each cluster
for l in memberlist:
    filename = choice(l)

    print filename

    img = Image.open(filename)
    img.show()

# save cluster member to text file
if saveToFile:
    with open(rootdir+'.txt','w') as f:
        cluster_id = 0
        for l in memberlist:
            f.write('Cluster '+ str(cluster_id)+'\n')
            f.write('--------------------------\n')
            for m in l:
                f.write(m)
                f.write('\n')
            f.write('==========================\n')
            cluster_id += 1
    
    
