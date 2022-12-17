import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup


from configparser import ConfigParser
import os
import sys
import requests

kivy.require('1.0.7')

global pathfile, config
pathfile = ''
config = ConfigParser()


class FileChooser(Screen):
    def select(self, *args):
        try: 
            self.button.text = 'Selected: ' + args[1][0]
        except: 
            pass
    def selected(self, *args):
        global pathfile
        pathfile = self.button.text.replace('Selected: ', '')
    
class mainLayout(Screen):
    
    global username, password, config
    username, password = '', ''
    
    def usernameInput(self):
        global username
        username = self.ids['username'].text
        
    def passwordInput(self):
        global password
        password = self.ids['password'].text
        
    def uploadBtn(self):
        global pathfile, username, password, config
        change = 0
        if config['HELIOS']['username'] != username and username != '':
            config['HELIOS']['username'] = username
            change = 1
        if config['HELIOS']['password'] != password and password != '': 
            config['HELIOS']['password'] = password
            change = 1
        if config['HELIOS']['pathfile'] != pathfile and pathfile != '':
            config['HELIOS']['pathfile'] = pathfile
            change = 1
        if change == 1:
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        if pathfile != '':
            if not os.path.exists(pathfile):
                Popup(title="Error", content=Label(text = "The folder didn't exist"), size_hint=(None, None), size=(200, 200)).open()
                return
            
            lab = pathfile[-2:]
            import UploadFilesOnHelios as UFOH
            uploadFiles = UFOH.UploadFilesOnHelios(pathfile, lab, username, password)
            uploadFiles.start()
            config['HELIOS']['pathfile'] =\
                config['HELIOS']['pathfile'][:-1] + str(int(config['HELIOS']['pathfile'][-1:]) + 1)\
                if \
                    int(config['HELIOS']['pathfile'][-1:]) < 9\
                else\
                    config['HELIOS']['pathfile'][:-2] + str((int(config['HELIOS']['pathfile'][-2:-1])+1)) +\
                        str((int(config['HELIOS']['pathfile'][-1:]) + 1) % 10)
            with open(os.path.dirname(os.path.realpath(__file__)) + '/config.ini', 'w') as configfile:
                config.write(configfile)
        else:
            Popup(title="Error", content=Label(text = "You didn't select any folder!"), size_hint=(None, None), size=(200, 200)).open()
        
class UploadAssistantApp(App):
    """
        This mini-app would allow users to upload files automatically on the Helios platform. They would insert their 
        username, password and then select the folder where the exercises are located. After this, the app will
        automatically save the username, password and the path. Then, if user hit upload button, app will start a web driver,
        and using selenium framework, the app will login into the Helios platform, search for specific laborator
        and after that, upload file one by one. The important thing is that the folder of the user should be saved 
        with last 2 character in the name, the number of the laborator. Because the app will use the last 2 characters
        from the folder name to search for the laborator (Example: Lab_08 / Lab_12 or Lab08 / Lab12)
        
        A feature of the app is that once you choose first time thhe path of the file, the app will automatically
        save the path, and next time you will use it, will automatically pass to the next lab and search in the 
        same folder for the next lab. In our examples will be Lab_09 / Lab_13 or Lab09 / Lab13. So, if you keep the folder
        with the files in the same folder, you will not have to choose the path again.
    """
    def build(self):
        global screen, sM, config, pathfile 
        
        self.Configuration()
        
        sM = ScreenManager()
        screen = [mainLayout(name='MainLayout'), FileChooser(name='FileChooser')]
        screen[0].ids['username'].text = config['HELIOS']['username']
        screen[0].ids['password'].text = config['HELIOS']['password']
        pathfile = config['HELIOS']['pathfile']
        
        
        self.mainLayoutScreen()
        
        return sM
    
    def chooseFolderScreen(self):
        global screen, sM
        sM.switch_to(screen[1], direction='left')
    
    def mainLayoutScreen(self):
        global screen, sM
        sM.switch_to(screen[0])
    
    def Configuration(self):
        global config
        os.chdir(sys.path[0])
        if not os.path.exists('config.ini'):
            config['HELIOS'] = {
                'username': '',
                'password': '',
                'pathfile': ''
            }
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        else:
            config.read('config.ini')
        
    
if __name__ == '__main__':
    UploadAssistantApp().run() 