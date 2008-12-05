from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import sys, os


qgis_prefix = "C:\qgis\Quantum GIS"

class Wizard(QWizard):
    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        self.setFixedSize(QSize(800,500))
        self.addPage(self.createIntroPage())
        self.addPage(self.createResolutionPage())
        self.addPage(self.createSampleDataPage())
        self.addPage(self.createControlDataPage())
        self.addPage(self.createDBConnectionPage())
        self.addPage(self.createImportingPage())

    
        
    def createIntroPage(self):
        page = QWizardPage()
        page.setTitle("Step 1: Region")
        
        # Project Description
        nameLabel = QLabel("Project Name")
        self.nameLineEdit = QLineEdit()
        nameLabel.setBuddy(self.nameLineEdit)
        locationLabel = QLabel("Project Location")
        self.locationComboBox = QComboBox()
        locationLabel.setBuddy(self.locationComboBox)
        locationBrowseButton = QPushButton("...")
        locationBrowseButton.setFixedSize(QSize(30,20))
        locationHLayout = QHBoxLayout()
        locationHLayout.addWidget(self.locationComboBox)
        locationHLayout.addWidget(locationBrowseButton)    
        descLabel = QLabel("Project Description")
        self.descTextEdit = QTextEdit()
        descLabel.setBuddy(self.descTextEdit)
        # Project Description Layout
        projectVLayout = QVBoxLayout()
        projectVLayout.addWidget(nameLabel)
        projectVLayout.addWidget(self.nameLineEdit)
        projectVLayout.addWidget(locationLabel)
        projectVLayout.addLayout(locationHLayout)
        projectVLayout.addWidget(descLabel)
        projectVLayout.addWidget(self.descTextEdit)
        # Selecting Counties using the tree widget
        self.countySelectTree = QTreeWidget()
        self.countySelectTree.setColumnCount(1)
        self.countySelectTree.setHeaderLabels(["State/County"])
        self.countySelectTree.setItemsExpandable(True)
        state = QTreeWidgetItem(self.countySelectTree, [QString("State")])
        county = QTreeWidgetItem(state, [QString("County")])
        state = QTreeWidgetItem(self.countySelectTree, [QString("State1")])
        county = QTreeWidgetItem(state, [QString("County1")])
        # Displaying counties and selecting counties using the map
        canvas = QgsMapCanvas()
        canvas.setCanvasColor(QColor(0,0,0))
        canvas.enableAntiAliasing(True)
        canvas.useQImageToRender(False)
        layerPath = "./data/NC_Selected_Counties.shp"
        #layerPath = "./data/county.shp"
        layerName = "NCSelectedCounties"
        layerProvider = "ogr"
        layer = QgsVectorLayer(layerPath, layerName, layerProvider)
        if not layer.isValid():
            return
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        canvas.setExtent(layer.extent())
        cl = QgsMapCanvasLayer(layer)
        layers = [cl]
        canvas.setLayerSet(layers)
        # Vertical layout of all elements
        vLayout = QVBoxLayout()
        vLayout.addLayout(projectVLayout)
        vLayout.addWidget(self.countySelectTree)
        # Horizontal layout of all elements
        hLayout = QHBoxLayout()
        hLayout.addLayout(vLayout)
        hLayout.addWidget(canvas)
        page.setLayout(hLayout)

        self.populateCountySelectTree()

        return page


    def populateCountySelectTree(self):
        pass



    def createResolutionPage(self):
        page = QWizardPage()
        page.setTitle("Step 2: Resolution of the Population Synthesis")

        resolutionLabel = QLabel("At what resolution do you want to synthesize the population (County/Tract/Blockgroup level)?")
        self.resolutionComboBox = QComboBox()
        self.resolutionComboBox.addItems([QString("County"), QString("Tract"), QString("Blockgroup")])
        self.resolutionComboBox.setFixedSize(QSize(250,20))

        geocorrGroupBox = QGroupBox("Will you provide Geographic Correspondence between the Geography and PUMA?")
        self.geocorrUserProvRadio = QRadioButton("Yes")
        self.geocorrAutoRadio = QRadioButton("No")
        self.geocorrUserProvRadio.setChecked(True)

        geocorrLocationLabel = QLabel("Location of the geographic correspondence file")
        self.geocorrLocationComboBox = QComboBox()
        geocorrLocationLabel.setBuddy(self.geocorrLocationComboBox)
        geocorrLocationBrowseButton = QPushButton("...")
        geocorrLocationBrowseButton.setFixedSize(QSize(30,20))
        geocorrLocationHLayout = QHBoxLayout()
        geocorrLocationHLayout.addWidget(self.geocorrLocationComboBox)
        geocorrLocationHLayout.addWidget(geocorrLocationBrowseButton)    

        geocorrHLayout = QHBoxLayout()
        geocorrHLayout.addWidget(self.geocorrUserProvRadio)
        geocorrHLayout.addWidget(self.geocorrAutoRadio)
        geocorrVLayout = QVBoxLayout()
        geocorrVLayout.addLayout(geocorrHLayout)
        geocorrVLayout.addWidget(geocorrLocationLabel)
        geocorrVLayout.addLayout(geocorrLocationHLayout)
        geocorrGroupBox.setLayout(geocorrVLayout)

        vLayout = QVBoxLayout()
        vLayout.addWidget(resolutionLabel)
        vLayout.addWidget(self.resolutionComboBox)
        vLayout.addWidget(geocorrGroupBox)
        page.setLayout(vLayout)

        return page

    def createSampleDataPage(self):
        page = QWizardPage()
        page.setTitle("Step 3: Population Sample")

        sampleGroupBox = QGroupBox("Will you provide the sample for population synthesis?")
        self.sampleUserProvRadio = QRadioButton("Yes")
        self.sampleAutoRadio = QRadioButton("No")
        self.sampleUserProvRadio.setChecked(True)

        sampleHHLocationLabel = QLabel("Location of the household sample")
        sampleGQLocationLabel = QLabel("Location of the groupquarter sample")
        samplePopLocationLabel = QLabel("Location of the population sample")
        
        self.sampleHHLocationComboBox = QComboBox()
        sampleHHLocationLabel.setBuddy(self.sampleHHLocationComboBox)
        sampleHHBrowseButton = QPushButton("...")
        sampleHHBrowseButton.setFixedSize(QSize(30,20))
        sampleHHLocationHLayout = QHBoxLayout()
        sampleHHLocationHLayout.addWidget(self.sampleHHLocationComboBox)
        sampleHHLocationHLayout.addWidget(sampleHHBrowseButton)

        
        self.sampleGQLocationComboBox = QComboBox()
        sampleGQLocationLabel.setBuddy(self.sampleGQLocationComboBox)
        sampleGQBrowseButton = QPushButton("...")
        sampleGQBrowseButton.setFixedSize(QSize(30,20))
        sampleGQLocationHLayout = QHBoxLayout()
        sampleGQLocationHLayout.addWidget(self.sampleGQLocationComboBox)
        sampleGQLocationHLayout.addWidget(sampleGQBrowseButton)

        

        self.samplePopLocationComboBox = QComboBox()
        samplePopLocationLabel.setBuddy(self.samplePopLocationComboBox)
        samplePopBrowseButton = QPushButton("...")
        samplePopBrowseButton.setFixedSize(QSize(30,20))
        samplePopLocationHLayout = QHBoxLayout()
        samplePopLocationHLayout.addWidget(self.samplePopLocationComboBox)
        samplePopLocationHLayout.addWidget(samplePopBrowseButton)

        sampleHLayout = QHBoxLayout()
        sampleHLayout.addWidget(self.sampleUserProvRadio)
        sampleHLayout.addWidget(self.sampleAutoRadio)
        sampleVLayout = QVBoxLayout()
        sampleVLayout.addLayout(sampleHLayout)
        sampleVLayout.addWidget(sampleHHLocationLabel)
        sampleVLayout.addLayout(sampleHHLocationHLayout)
        sampleVLayout.addWidget(sampleGQLocationLabel)
        sampleVLayout.addLayout(sampleGQLocationHLayout)
        sampleVLayout.addWidget(samplePopLocationLabel)
        sampleVLayout.addLayout(samplePopLocationHLayout)
        
        sampleGroupBox.setLayout(sampleVLayout)

        vLayout = QVBoxLayout()
        vLayout.addWidget(sampleGroupBox)
        page.setLayout(vLayout)

        return page



    def createControlDataPage(self):
        page = QWizardPage()
        page.setTitle("Step 4: Control Totals")
        controlGroupBox = QGroupBox("Will you provide the control variable totals for population synthesis?")
        self.controlUserProvRadio = QRadioButton("Yes")
        self.controlAutoRadio = QRadioButton("No")
        self.controlUserProvRadio.setChecked(True)

        controlHHLocationLabel = QLabel("Location of the household control totals")
        controlGQLocationLabel = QLabel("Location of the groupquarter control totals")
        controlPopLocationLabel = QLabel("Location of the population control totals")
        
        self.controlHHLocationComboBox = QComboBox()
        controlHHLocationLabel.setBuddy(self.controlHHLocationComboBox)
        controlHHBrowseButton = QPushButton("...")
        controlHHBrowseButton.setFixedSize(QSize(30,20))
        controlHHLocationHLayout = QHBoxLayout()
        controlHHLocationHLayout.addWidget(self.controlHHLocationComboBox)
        controlHHLocationHLayout.addWidget(controlHHBrowseButton)

        
        self.controlGQLocationComboBox = QComboBox()
        controlGQLocationLabel.setBuddy(self.controlGQLocationComboBox)
        controlGQBrowseButton = QPushButton("...")
        controlGQBrowseButton.setFixedSize(QSize(30,20))
        controlGQLocationHLayout = QHBoxLayout()
        controlGQLocationHLayout.addWidget(self.controlGQLocationComboBox)
        controlGQLocationHLayout.addWidget(controlGQBrowseButton)

        

        self.controlPopLocationComboBox = QComboBox()
        controlPopLocationLabel.setBuddy(self.controlPopLocationComboBox)
        controlPopBrowseButton = QPushButton("...")
        controlPopBrowseButton.setFixedSize(QSize(30,20))
        controlPopLocationHLayout = QHBoxLayout()
        controlPopLocationHLayout.addWidget(self.controlPopLocationComboBox)
        controlPopLocationHLayout.addWidget(controlPopBrowseButton)

        controlHLayout = QHBoxLayout()
        controlHLayout.addWidget(self.controlUserProvRadio)
        controlHLayout.addWidget(self.controlAutoRadio)
        controlVLayout = QVBoxLayout()
        controlVLayout.addLayout(controlHLayout)
        controlVLayout.addWidget(controlHHLocationLabel)
        controlVLayout.addLayout(controlHHLocationHLayout)
        controlVLayout.addWidget(controlGQLocationLabel)
        controlVLayout.addLayout(controlGQLocationHLayout)
        controlVLayout.addWidget(controlPopLocationLabel)
        controlVLayout.addLayout(controlPopLocationHLayout)
        
        controlGroupBox.setLayout(controlVLayout)

        vLayout = QVBoxLayout()
        vLayout.addWidget(controlGroupBox)
        page.setLayout(vLayout)

        return page



    def createDBConnectionPage(self):
        page = QWizardPage()
        page.setTitle("Step 5: MySQL Connection Settings")


        hostnameLabel = QLabel("Hostname")
        self.hostnameLineEdit = QLineEdit()
        hostnameLabel.setBuddy(self.hostnameLineEdit)
        hostnameHLayout = QHBoxLayout()
        hostnameHLayout.addWidget(hostnameLabel)
        hostnameHLayout.addWidget(self.hostnameLineEdit)

        usernameLabel = QLabel("Username")
        self.usernameLineEdit = QLineEdit()
        usernameLabel.setBuddy(self.usernameLineEdit)
        usernameHLayout = QHBoxLayout()
        usernameHLayout.addWidget(usernameLabel)
        usernameHLayout.addWidget(self.usernameLineEdit)

        passwordLabel = QLabel("Password")
        self.passwordLineEdit = QLineEdit()
        passwordLabel.setBuddy(self.passwordLineEdit)
        passwordHLayout = QHBoxLayout()
        passwordHLayout.addWidget(passwordLabel)
        passwordHLayout.addWidget(self.passwordLineEdit)
        
        
        vLayout = QVBoxLayout()
        vLayout.addLayout(hostnameHLayout)
        vLayout.addLayout(usernameHLayout)
        vLayout.addLayout(passwordHLayout)
        page.setLayout(vLayout)

        return page


    def createImportingPage(self):
        page = QWizardPage()
        page.setTitle("Step 6: Importing Data...")
        
        progressBar = QProgressBar()

        layout = QVBoxLayout()
        layout.addWidget(progressBar)
        page.setLayout(layout)

        return page


def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    wizard = Wizard()
    

    wizard.show()
    app.exec_()

    QgsApplication.exitQgis()


main()
    
