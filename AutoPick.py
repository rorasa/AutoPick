import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar

from PIL import Image
from PIL import ImageColor
from sklearn.cluster import KMeans
import numpy as np

import os, os.path
import time
from random import choice

collage_size = 1024

def gatherValidFiles(path):
    filelist = []
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path,f)):
            if not f.startswith('.'):
                if f.lower().endswith(('.png','.jpg','.jpeg','.bmp','.tif')):
                    filelist.append(os.path.join(path,f))
        
    return filelist

def getHistograms(filelist):
    hist = []

    # create histogram for each photo
    for f in filelist:
        print('Analysing: '+f)
        img = Image.open(f)
        h = img.histogram()
        hist.append(np.array(h))

    hist = np.stack(hist)
    print('Finished')
    return hist

def doClustering(hist,no_clusters):
    # perform KMeans clustering
    print('Clustering data')
    kmeans = KMeans(n_clusters=no_clusters).fit(hist)
    labels = kmeans.labels_

    print('Finished')

    return labels

def createGroups(filelist,labels, total_groups):
    groups = []
    for i in range(0, total_groups):
        groups.append(list())

    for i in range(0,len(filelist)):
        groups[labels[i]].append(filelist[i])

    return groups

def makeCollage(groups, layout):
    imagelist = []
    for group in groups:
        f = choice(group)
        imagelist.append(f)
        
    collage = Image.new('RGB', (collage_size,collage_size), color='#ffffff')

    if(layout==2):
        height = 476
        width = 976
        box = [(24,24),(24,524)]
    elif(layout==3):
        height = 309
        width = 976
        box = [(24,24),(24,357),(24,690)]
    elif(layout==4):
        height = 476
        width = 476
        box = [(24,24),(524,24),(24,524),(524,524)]
    elif(layout==6):
        height = 309
        width = 476
        box = [(24,24),(524,24),(24,357),(524,357),(24,690),(524,690)]
    elif(layout==9):
        height = 309
        width = 309
        box = [(24,24),(357,24),(690,24),(24,357),(357,357),(690,357),(24,690),(357,690),(690,690)]
        

    for i in range(0,layout):
        f = imagelist[i]
        img = Image.open(f)
        img.thumbnail((max(width,height),max(width,height)))
        
        half_width = img.size[0]/2
        half_height = img.size[1]/2
        img = img.crop((half_width - (width/2),half_height - (height/2), half_width + (width/2), half_height + (height/2)))
        
        collage.paste(img, box[i])
                        
    collage.show()
        
        
        

    #for i in range(0,layout):
    ##    img = Image.open(imagelist[i])
    #    img.thumbnail((collage_size,collage_size))
        
    #    img.show()
        
class MainWindow(FloatLayout):
    ''' Controller class for the GUI handlers of the main GUI window
    '''
    info = StringProperty()
    #label_1 = ObjectProperty()
    #label_2 = ObjectProperty()
    label_folder_name = ObjectProperty()
    label_total_images = ObjectProperty()
    label_est_time = ObjectProperty()
    layout_image = ObjectProperty()

    layout = 4;
    
    def newProject(self):
        ''' Open a dialog to choose the project folder,
        the folder path is stored and its statistics computed, then
        update the UI accourdingly.
        '''
        content = OpenDialog(select=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title='Open new project', content=content,  size_hint=(0.9,0.9))
        self._popup.open()

    def saveCollage(self):
        print('clicked - Save Collage')

    def startAnalysis(self):
        self.histograms = getHistograms(self.filelist)

    def startClustering(self):
        self.labels = doClustering(self.histograms, self.layout)        
        self.groups = createGroups(self.filelist, self.labels, self.layout)

        makeCollage(self.groups,self.layout)
        
    def dismiss_popup(self):
        self._popup.dismiss()

    def chooseLayout(self):
        content = ChooseLayout(getLayout=self.getLayout)
        self._popup = Popup(title='Choose collage layout', content=content, size_hint=(0.9,0.5))
        self._popup.open()

    def getLayout(self,layout_id):
        self.layout = layout_id

        self.layout_image.source = 'group'+str(layout_id)+'.png'

        self.dismiss_popup()

    def load(self,path,filename):
        ''' Read the path from argument, compute its statistic and update the UI
        '''
        print('Selecting folder: '+path)
        
        # gather the list of images files
        self.path = path
        self.filelist = gatherValidFiles(path)

        # estimate time required to compute one image
        time_start = time.clock()
        img = Image.open(self.filelist[0])
        img.histogram()
        time_taken = time.clock()-time_start
        
        # Update UI
        self.label_folder_name.text = os.path.split(path)[1]
        self.label_total_images.text = str(len(self.filelist))
        est_time = round(time_taken * len(self.filelist) * 1.1)
        self.label_est_time.text = str(est_time)+' seconds'

        self.dismiss_popup()

class OpenDialog(FloatLayout):
    select = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def is_dir(self, path, filename):
        return os.path.isdir(os.path.join(path,filename))
    def home_dir(self):
        return os.path.expanduser('~')

class ChooseLayout(FloatLayout):
    getLayout = ObjectProperty(None)

class AutoPick(App):

    def build(self):
       # return Label(text='Hello World')
        return MainWindow(info='Hello World')

if __name__ == '__main__':
    AutoPick().run()
