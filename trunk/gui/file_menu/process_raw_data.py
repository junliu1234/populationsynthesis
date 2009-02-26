from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
import shutil, urllib, os


class PopulateFileManager():
    def __init__(self, project, fileManager):
        self.project = project
        self.fileManager = fileManager
        self.fileManager.setEnabled(True)
        self.fileManager.clear()
        self.PopulateTree()
        

    def PopulateTree(self):
        projectAncestor = QTreeWidgetItem(self.fileManager, [QString(self.project.name)])
        informationParent = QTreeWidgetItem(projectAncestor, [QString("Information")])
        
        dummy = ""
        if self.project.region is not None:
            for i in self.project.region:
                dummy = dummy + i.text(0) + ", "+ i.parent().text(0)+ "; "

        informationItems = {"Location":self.project.location, 
                            "Description":self.project.description,
                            "Region":dummy}
        for i,j in informationItems.items():
            child = QTreeWidgetItem(informationParent, [i, QString(j)])
        
        geocorrParent = QTreeWidgetItem(projectAncestor, [QString("Geographic Correspondence")])
        geocorrItems = {"User Provided":self.project.geocorrUserProv.userProv, 
                        "Location":self.project.geocorrUserProv.location}
        
        for i,j in geocorrItems.items():
            child = QTreeWidgetItem(geocorrParent, [i, QString("%s"%j)])

        sampleParent = QTreeWidgetItem(projectAncestor, [QString("Sample")])
        sampleItems = {"User Provided":self.project.sampleUserProv.userProv,
                       "Household Data Location": self.project.sampleUserProv.hhLocation,
                       "GQ Data Location": self.project.sampleUserProv.gqLocation,
                       "Person Data Location": self.project.sampleUserProv.popLocation}

        for i,j in sampleItems.items():
            child = QTreeWidgetItem(sampleParent, [i, QString("%s"%j)])

        controlParent = QTreeWidgetItem(projectAncestor, [QString("Control")])
        controlItems = {"User Provided":self.project.controlUserProv.userProv,
                       "Household Data Location": self.project.controlUserProv.hhLocation,
                       "GQ Data Location": self.project.controlUserProv.gqLocation,
                       "Person Data Location": self.project.controlUserProv.popLocation}

        for i,j in controlItems.items():
            child = QTreeWidgetItem(controlParent, [i, QString("%s"%j)])

        dbParent = QTreeWidgetItem(projectAncestor, [QString("Database")])
        dbItems = {"Hostname":self.project.db.hostname,
                   "Username":self.project.db.username,
                   "Password":self.project.db.password}

        for i,j in dbItems.items():
            child = QTreeWidgetItem(dbParent, [QString(i), QString(j)])

        self.fileManager.expandItem(projectAncestor)
        self.fileManager.expandItem(informationParent)
        self.fileManager.expandItem(geocorrParent)
        self.fileManager.expandItem(sampleParent)
        self.fileManager.expandItem(controlParent)
        self.fileManager.expandItem(dbParent)
        
    def UpdateTree(self):
        pass

class PrepareData():
    
    def __init__(self, project):
        self.project = project
        self.selectedCounties()
        self.downloadPUMSFiles()
        self.downloadSFFiles()
        self.importToSQL()
        


        for i in wizard.project.region:
            print i.parent().text(0)

            projectDB = createDBC(wizard.project.db)           
            if not projectDB.dbc.open():
                QMessageBox.warning(None, "oisdf", 
                                    QString("Database Error: %1").arg(projectDB.dbc.lastError().text()))
                
            else:
                QMessageBox.warning(None, "oisdf", 
                                    QString("Found"))
            projectDB.dbc.close()
            projectDB.dbc.removeDatabae()

    def selectedCounties(self):
        pass

    def downloadPUMSFiles(self):
        pass

    def downloadSFFiles(self):
        pass

    def convertRawPUMSData(self):
        pass

    def importToSQL(self):
        pass

    
        

    
