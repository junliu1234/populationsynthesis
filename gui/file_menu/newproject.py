from PyQt4.QtCore import *
from PyQt4.QtGui import *



class Geocorr(object):
    def __init__(self, userprov=None, geocorrLocation=None):
        self.userProv = userprov
        if userprov:
            self.location = geocorrLocation
        else:
            self.location = QString("./data/geocorr.csv")

class Sample(object):
    def __init__(self, userprov=None, sampleHHLocation=None, sampleGQLocation=None, samplePopLocation=None):
        self.userProv = userprov
        if userprov:
            self.hhLocation = sampleHHLocation
            self.gqLocation = sampleGQLocation
            self.popLocation = samplePopLocation
        else:
            self.hhLocation = QString("./data/sampleHH.csv")
            self.gqLocation = QString("./data/sampleGQ.csv")
            self.popLocation = QString("./data/samplePop.csv")

class Control(object):
    def __init__(self, userprov=None, controlHHLocation=None, controlGQLocation=None, controlPopLocation=None):
        self.userProv = userprov
        if userprov:
            self.hhLocation = controlHHLocation
            self.gqLocation = controlGQLocation
            self.popLocation = controlPopLocation
        else:
            self.hhLocation = QString("./data/controlHH.csv")
            self.gqLocation = QString("./data/controlGQ.csv")
            self.popLocation = QString("./data/controlPop.csv")


class DBInfo(object):
    def __init__(self, hostname=None, username=None, password=None, driver="QMYSQL"):
        self.driver = driver
        self.hostname = hostname
        self.username = username
        self.password = password



class NewProject(object):
    def __init__(self, name=None, location=None, description=None, region=None, resolution=None, geocorrUserProv=Geocorr(), 
                 sampleUserProv=Sample(), controlUserProv=Control(), db = DBInfo()):
        self.name = name
        self.location = location
        self.description = description
        self.region = region
        self.resolution = resolution
        self.geocorrUserProv = geocorrUserProv
        self.sampleUserProv = sampleUserProv
        self.controlUserProv = controlUserProv
        self.db = db


class Geocorr(object):
    def __init__(self, userprov=None, geocorrLocation=None):
        self.userProv = userprov
        if userprov:
            self.location = geocorrLocation
        else:
            self.location = QString("./data/geocorr.csv")

class Sample(object):
    def __init__(self, userprov=None, sampleHHLocation=None, sampleGQLocation=None, samplePopLocation=None):
        self.userProv = userprov
        if userprov:
            self.hhLocation = sampleHHLocation
            self.gqLocation = sampleGQLocation
            self.popLocation = samplePopLocation
        else:
            self.hhLocation = QString("./data/sampleHH.csv")
            self.gqLocation = QString("./data/sampleGQ.csv")
            self.popLocation = QString("./data/samplePop.csv")

class Control(object):
    def __init__(self, userprov=None, controlHHLocation=None, controlGQLocation=None, controlPopLocation=None):
        self.userProv = userprov
        if userprov:
            self.hhLocation = controlHHLocation
            self.gqLocation = controlGQLocation
            self.popLocation = controlPopLocation
        else:
            self.hhLocation = QString("./data/controlHH.csv")
            self.gqLocation = QString("./data/controlGQ.csv")
            self.popLocation = QString("./data/controlPop.csv")




            
            
    
        
