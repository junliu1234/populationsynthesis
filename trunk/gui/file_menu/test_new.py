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

        self.connect(self.locationComboBox, SIGNAL("currentIndexChanged(int)"), self.selectFolder)

           
    def createIntroPage(self):
        page = QWizardPage()
        page.setTitle("Step 1: Region")
        
        # Project Description
        nameLabel = QLabel("Project Name")
        self.nameLineEdit = QLineEdit()
        nameLabel.setBuddy(self.nameLineEdit)
        locationLabel = QLabel("Project Location")
        self.locationComboBox = QComboBox()
        self.locationComboBox.addItems([QString(" "), QString("Browse to select folder...")])
        locationLabel.setBuddy(self.locationComboBox)
        descLabel = QLabel("Project Description")
        self.descTextEdit = QTextEdit()
        descLabel.setBuddy(self.descTextEdit)
        # Project Description Layout
        projectVLayout = QVBoxLayout()
        projectVLayout.addWidget(nameLabel)
        projectVLayout.addWidget(self.nameLineEdit)
        projectVLayout.addWidget(locationLabel)
        projectVLayout.addWidget(self.locationComboBox)
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
        #layerPath = "./data/NC_Selected_Counties.shp"
        layerPath = "./data/county.shp"
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

    def selectFolder(self):
        location = "1"
        count = self.locationComboBox.count()
        print count, self.locationComboBox.currentIndex()
        if self.locationComboBox.currentText() == "Browse to select folder...":
            #location = QFileDialog.getExistingDirectory(self, QString("Project Location"), "C:/", QFileDialog.ShowDirsOnly)
            self.locationComboBox.insertItem(1, QString(location))
            self.locationComboBox.setCurrentIndex(1)




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

        geocorrLocationLabel = QLabel("Select the geographic correspondence file")
        self.geocorrLocationComboBox = QComboBox()
        self.geocorrLocationComboBox.addItems([QString(" "), QString("Browse to select folder...")])
        geocorrLocationLabel.setBuddy(self.geocorrLocationComboBox)


        geocorrHLayout = QHBoxLayout()
        geocorrHLayout.addWidget(self.geocorrUserProvRadio)
        geocorrHLayout.addWidget(self.geocorrAutoRadio)
        geocorrVLayout = QVBoxLayout()
        geocorrVLayout.addLayout(geocorrHLayout)
        geocorrVLayout.addWidget(geocorrLocationLabel)
        geocorrVLayout.addWidget(self.geocorrLocationComboBox)
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

        sampleHHLocationLabel = QLabel("Select the household sample file")
        sampleGQLocationLabel = QLabel("Select the groupquarter sample file")
        samplePopLocationLabel = QLabel("Select the population sample file")
        
        self.sampleHHLocationComboBox = QComboBox()
        self.sampleHHLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        sampleHHLocationLabel.setBuddy(self.sampleHHLocationComboBox)
        
        self.sampleGQLocationComboBox = QComboBox()
        self.sampleGQLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        sampleGQLocationLabel.setBuddy(self.sampleGQLocationComboBox)

        self.samplePopLocationComboBox = QComboBox()
        self.samplePopLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        samplePopLocationLabel.setBuddy(self.samplePopLocationComboBox)

        sampleHLayout = QHBoxLayout()
        sampleHLayout.addWidget(self.sampleUserProvRadio)
        sampleHLayout.addWidget(self.sampleAutoRadio)
        sampleVLayout = QVBoxLayout()
        sampleVLayout.addLayout(sampleHLayout)
        sampleVLayout.addWidget(sampleHHLocationLabel)
        sampleVLayout.addWidget(self.sampleHHLocationComboBox)
        sampleVLayout.addWidget(sampleGQLocationLabel)
        sampleVLayout.addWidget(self.sampleGQLocationComboBox)
        sampleVLayout.addWidget(samplePopLocationLabel)
        sampleVLayout.addWidget(self.samplePopLocationComboBox)
        
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

        controlHHLocationLabel = QLabel("Select the household control total file")
        controlGQLocationLabel = QLabel("Select the groupquarter control total file")
        controlPopLocationLabel = QLabel("Select the population control total file")
        
        self.controlHHLocationComboBox = QComboBox()
        self.controlHHLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        controlHHLocationLabel.setBuddy(self.controlHHLocationComboBox)
        
        self.controlGQLocationComboBox = QComboBox()
        self.controlGQLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        controlGQLocationLabel.setBuddy(self.controlGQLocationComboBox)

        self.controlPopLocationComboBox = QComboBox()
        self.controlPopLocationComboBox.addItems([QString(" "), QString("Browse to select file...")])
        controlPopLocationLabel.setBuddy(self.controlPopLocationComboBox)


        controlHLayout = QHBoxLayout()
        controlHLayout.addWidget(self.controlUserProvRadio)
        controlHLayout.addWidget(self.controlAutoRadio)
        controlVLayout = QVBoxLayout()
        controlVLayout.addLayout(controlHLayout)
        controlVLayout.addWidget(controlHHLocationLabel)
        controlVLayout.addWidget(self.controlHHLocationComboBox)
        controlVLayout.addWidget(controlGQLocationLabel)
        controlVLayout.addWidget(self.controlGQLocationComboBox)
        controlVLayout.addWidget(controlPopLocationLabel)
        controlVLayout.addWidget(self.controlPopLocationComboBox)
        
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
    wiz = Wizard()
    

    wiz.show()
    app.exec_()

    QgsApplication.exitQgis()


if __name__ == "__main__":
    main()
    
