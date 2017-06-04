import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty

class MainWindow(FloatLayout):
    ''' Controller class for the GUI handlers of the main GUI window
    '''
    info = StringProperty()
    #label_1 = ObjectProperty()
    #label_2 = ObjectProperty()

    def newProject(self):
        print('clicked - New Project')

    def saveCollage(self):
        print('clicked - Save Collage')

    def startAnalysis(self):
        print('clicked - Start Analysis')
    #def do_action(self):
    #    self.label_1.text = 'Fuck is Kivy'
    #    self.label_2.text = 'Fuck it Confusing KV file'    

class AutoPick(App):

    def build(self):
       # return Label(text='Hello World')
        return MainWindow(info='Hello World')

if __name__ == '__main__':
    AutoPick().run()
