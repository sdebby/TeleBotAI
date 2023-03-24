import logging
import os

logging.basicConfig(level=logging.INFO)

class FileHelper():
    def WriteToFile(fn:str,txt:str): # this will write text to log file
        """
        Write to file\n
        - fn: file name\n
        - txt: text to write
        """
        with open(fn, "a") as file1:
            file1.write(txt+ '\n')
        file1.close
        logging.info('Writing into file: '+fn)

    def ReadFile(fn:str):
            """
            Read from file\n
            - fn: file name \n
            Return file content
            """
            try:
                with open(fn,"r") as text:
                    res=text.read()
            except:
                logging.error('Error opening file')
            return res
    
    def ReadConfigFile(fn:str): #read user data
        """
        Read config file\n
        - fn: file name \n
        - '#' will be ignored\n
        - new lines will be ignored\n
        Return dict
        """
        res = {}
        try:
            with open(fn,"r") as text:
                for line in text:
                    if not line[0]=='#' and not line=='\n': #remove comments and new lines
                        key, value = line.split('=')
                        if len(key)>1 :     
                                if value[-1]=='\n': res[key] = value[:-1]
                                else: res[key] = value
        except:
            logging.error('Error opening config file')
        return res