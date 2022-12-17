import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import logging
import sys
from threading import Thread



class CustomFormatter(logging.Formatter):
   
   format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

   FORMATS = {
      logging.DEBUG: format,
      logging.INFO:  format,
      logging.WARNING: format,
      logging.ERROR: format,
      logging.CRITICAL: format
   }

   def format(self, record):
      log_fmt = self.FORMATS.get(record.levelno)
      formatter = logging.Formatter(log_fmt)
      return formatter.format(record)
     
class UploadFilesOnHelios(Thread):
   driverpathchrome = 'Driver/chromedriver'
   
   def __init__(self, pathfile, lab, username, password):
      Thread.__init__(self)
      self.pathfile = pathfile
      self.lab = lab
      self.username = username
      self.password = password
      self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
      
      logger = logging.getLogger()
      logger.setLevel(logging.ERROR)
      handler = logging.FileHandler('UploadAssistant.log')
      handler.setFormatter(CustomFormatter())
      logger.addHandler(handler)
      
   #convert file from C to txt
   def convertCtoTXT(self, path, lab):
      if not os.path.exists(path + '/lab-%s-TXT-files' % lab):
         os.mkdir(path + '/lab-%s-TXT-files' % lab)
      
      for file in os.listdir(path):
         if file.endswith('.c'):
            shutil.copy(path + '/' + file, path + '/lab-%s-TXT-files/%s.txt' % (lab, file[:-2]))   
      
   def loginHelios(self, username, password):
      
      #Open browser
      self.driver.get("https://helios.utcluj.ro/LEARN2CODE/login.php?SID")
      #LOGIN 
      try:   
         nameBox = self.driver.find_element(By.NAME, "username")
         nameBox.send_keys(username)
         passwordBox = self.driver.find_element(By.NAME, "password")
         passwordBox.send_keys(password)
         passwordBox.send_keys(Keys.RETURN)
      except Exception as e:
         logging.error("[ERROR]:" + e)
         

   def uploadFiles(self, filepath, lab):
      try:
         #Search for work area button
         try:
            menu = self.driver.find_elements(By.CLASS_NAME, "left_menu_div1")
            for button in menu:
               if 'work area' in button.text.lower():
                  button.click()
                  break
         except Exception as e:
            logging.error(e)
            
         #Upload files to laborator - take all file one by one and upload it
         os.chdir(filepath+'/lab-%s-TXT-files/' % lab)
         for file in os.listdir():
            #Search for a specific laborator by class name of td tag
            #The upload link will be on the next td (table cell)
            tds = self.driver.find_elements(By.CLASS_NAME, "results_table_content_td")
            #search for laborator
            index = 0
            for td in tds:
               if 'l'+lab in td.text.lower():
                  break
               index += 1
            try:
               #press add new file button
               td = tds[index+1]
               link_upload = td.find_element(By.CLASS_NAME, "href2")
               link_upload.click()
            except Exception as e:
               logging.error(e)
               break
               
            #upload file
            try:
               file_upload = self.driver.find_element(By.CLASS_NAME, "input1")
               file_upload.send_keys(filepath + '/lab-%s-TXT-files/%s' % (lab, file))

               send_btn = self.driver.find_element(By.CLASS_NAME, "button1")
               send_btn.click()
            except Exception as e:
               logging.error(e)
         
      except Exception as e:
         logging.error(e)
         
   def run(self):
      self.convertCtoTXT(self.pathfile, self.lab)
      self.loginHelios(self.username, self.password)
      self.uploadFiles(self.pathfile, self.lab)