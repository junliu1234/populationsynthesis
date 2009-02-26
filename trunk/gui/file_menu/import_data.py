from __future__ import with_statement
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import urllib
import os

from database.createDBConnection import createDBC


class importData():
    def __init__(self, filePath, varNamesDummy=False, varDescDummy=False):
        self.filePath = filePath
        self.varNamesDummy = varNamesDummy
        self.varDescDummy = varDescDummy
        self.createImportQuery()

    def createImportQuery(self):
        if self.varNamesDummy == True:
            if self.varDescDummy == True:
                with open("c:/SynTest/test.dat", 'r') as f:
                    for line in f:
                        pass
                print "names and desc"
            else:
                print "names and no desc"
                
        else:
            print "no names and no desc"


            #def 

class autoProcessPUMSData():
    def __init__(self, project):
        self.project = project
        self.states()
        self.downloadPUMSData()
        self.importPUMSData()

    def states(self):
        self.statesSelected = []
        for i in self.project.region:
            try:
                self.statesSelected.index(i.parent().text(0))
            except ValueError, e:
                self.statesSelected.append(i.parent().text(0))

    def downloadPUMSData(self):
        for i in self.statesSelected:
            try:
                os.makedirs("C:/HIPGen/data/%s"%i)
                urllib.urlretrieve("""http://ftp2.census.gov/census_2000/datasets/"""
                                   """PUMS/FivePercent/%s/PUMS5_04.TXT""" %i, 
                                   "C:/HIPGen/data/%s/PUMS5_04.TXT" %i)
            except WindowsError, e:
                reply = QMessageBox.question(None, "HIPGen: Processing Data", 
                                             QString("""Windows Error: %s.\n\n"""
                                                     """Do you wish to keep the existing files?"""
                                                     """\nPress No if you wish to download the files again."""%e), 
                                             QMessageBox.Yes|QMessageBox.No)
                if reply == QMessageBox.No:
                    confirm = QMessageBox.question(None, "HipGen: Processing Data", 
                                                   QString("""Are you sure you want to continue?"""),
                                                   QMessageBox.Yes|QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        urllib.urlretrieve("""http://ftp2.census.gov/census_2000/datasets/"""
                                           """PUMS/FivePercent/%s/PUMS5_04.TXT""" %i, 
                                           "C:/HIPGen/data/%s/PUMS5_04.TXT" %i)
                

    def importPUMSData(self):
        projectDBC = createDBC(self.project.db, self.project.name)
        
        projectDBC.dbc.open()
        query = QSqlQuery(projectDBC.dbc)
        print projectDBC.dbc.databaseName()
        for i in self.statesSelected:
            if query.exec_("""create table pumsraw%s (raw text)""" %i):
                query.exec_("""load data local infile 'C:/HIPGen/data/%s/PUMS5_04.TXT' """
                            """into table pumsraw%s""" %(i,i))
        projectDBC.dbc.close()

if __name__ == "__main__":
    importData("c:/SynTest/test.dat", True, True)
    autoProcessPUMSData("Arizona")
             
        
    
