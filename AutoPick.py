import kivy
from kivy.app import App
from kivy.cache import Cache
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KImage
from kivy.uix.progressbar import ProgressBar

from PIL import Image
from PIL import ImageColor
from PIL import ExifTags
from sklearn.cluster import KMeans
import numpy as np
from math import floor

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
    elif(layout==1):
        height = 976
        width = 976
        box = [(24,24)]
        
    for i in range(0,layout):
        f = imagelist[i]
        img = Image.open(f)

        # check ExifTags to correct image orientation
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(img._getexif().items())

        if exif[orientation] == 3:
            img = img.rotate(180, expand=True)
        elif exif[orientation] == 6:
            img = img.rotate(270, expand=True)
        elif exif[orientation] == 8:
            img = img.rotate(90, expand=True)

        # scale down the image to appropriate size
        if img.width >= img.height:
            if width > height:
                scale = width/img.width
            else:
                scale = height/img.height
        else:
            scale = width/img.width

        img_scaled = img.resize((floor(img.width*scale),floor(img.height*scale)))

        # crop image according to the layout
        left = floor((img_scaled.width-width)/2)
        upper = floor((img_scaled.height-height)/2)
        right = floor(img_scaled.width-((img_scaled.width-width)/2))
        lower = floor(img_scaled.height-((img_scaled.height-height)/2))

        print((width,height))
        print((img.width,img.height))
        print((img_scaled.width,img_scaled.height))
        print((left,upper,right,lower))

        img_cropped = img_scaled.copy().crop((left,upper,right,lower))
        
        collage.paste(img_cropped, box[i])
                        
    #collage.show()
    return collage
        
class MainWindow(FloatLayout):
    ''' Controller class for the GUI handlers of the main GUI window
    '''
    info = StringProperty()
    label_folder_name = ObjectProperty()
    label_total_images = ObjectProperty()
    label_est_time = ObjectProperty()
    layout_image = ObjectProperty()
    main_view = ObjectProperty()
    panel_analysis = ObjectProperty()
    panel_cluster = ObjectProperty()
    button_save = ObjectProperty()
    
    layout = 4;

    collage = Image.new('RGB',(1024,1024))
    
    def newProject(self):
        ''' Open a dialog to choose the project folder,
        the folder path is stored and its statistics computed, then
        update the UI accourdingly.
        '''
        content = OpenDialog(select=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title='Open new project', content=content,  size_hint=(0.9,0.9))
        self._popup.open()

    def saveCollage(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title='Save as', content=content, size_hint=(0.9,0.9))
        self._popup.open()

    def startAnalysis(self):
        self.progress_bar = ProgressDialog()
        self._popup = Popup(title='Analysing', content=self.progress_bar, size_hint=(0.9,0.5))
        self._popup.open()
        self.progress_bar.setMax(len(self.filelist))

        self.currentFile = 0
        self.histograms = []

        Clock.schedule_once(self.computeHistogram)
        
    def computeHistogram(self,dt):
        # create histogram for each photo
        f = self.filelist[self.currentFile]
        print('Analysing: '+ f)
        self.progress_bar.updateProgress(self.currentFile)
        
        img = Image.open(f)
        h = img.histogram()
        self.histograms.append(np.array(h))

        self.currentFile += 1
        if not (self.currentFile>=len(self.filelist)):
            Clock.schedule_once(self.computeHistogram)
        else:
            self.panel_cluster.disabled = False
            self.dismiss_popup()
        
    def startClustering(self):
        hist = np.stack(self.histograms)

        if (self.layout>len(self.filelist)):
            self.layout = 1
        
        self.labels = doClustering(hist, self.layout)        
        self.groups = createGroups(self.filelist, self.labels, self.layout)

        self.collage = makeCollage(self.groups,self.layout)
        self.collage.save(os.path.join(self.path,'collage.jpg'),'JPEG')

        self.main_view.clear_widgets()
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        
        image = KImage(source=os.path.join(self.path,'collage.jpg'))
        self.main_view.add_widget(image)

        self.button_save.disabled = False

        os.remove(os.path.join(self.path,'collage.jpg'))
        
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
        self.panel_analysis.disabled = False

        self.dismiss_popup()

    def save(self, path, filename):
        print('Saving to '+os.path.join(path,filename))

        self.collage.save(os.path.join(path,filename))

        self.dismiss_popup()

class OpenDialog(FloatLayout):
    select = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def is_dir(self, path, filename):
        return os.path.isdir(os.path.join(path,filename))
    def home_dir(self):
        return os.path.expanduser('~')

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def home_dir(self):
        return os.path.expanduser('~')
    
class ProgressDialog(FloatLayout):
    update = ObjectProperty(None)
    progress_bar = ObjectProperty(None)

    def updateProgress(self,value):
        self.progress_bar.value = value
        self.progress_bar.canvas.ask_update()

    def setMax(self, value):
        self.progress_bar.max = value

class ChooseLayout(FloatLayout):
    getLayout = ObjectProperty(None)

class AutoPick(App):

    def build(self):
       # return Label(text='Hello World')
        return MainWindow(info='Hello World')

if __name__ == '__main__':
    AutoPick().run()
