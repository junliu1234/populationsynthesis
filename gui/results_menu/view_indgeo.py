# PopGen 1.1 is A Synthetic Population Generator for Advanced
# Microsimulation Models of Travel Demand
# Copyright (C) 2009, Arizona State University
# See PopGen/License

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *
from newproject import Geography
from misc.map_toolbar import *
from results_preprocessor import *

# Inputs for this module
resultsloc = "C:/populationsynthesis/gui/results"
resultmap = "bg04_selected.shp"

class Indgeo(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.setMinimumSize(QSize(1000,500))
        self.setWindowTitle("Individual Geography Statistics")
        self.setWindowIcon(QIcon("./images/individualgeo.png"))
        self.project = project
        self.valid = False
        check = self.isValid()
        if check < 0:
            self.valid = True
            if self.project.resolution == "County":
                self.res_prefix = "co"
            if self.project.resolution == "Tract":
                self.res_prefix = "tr"
            if self.project.resolution == "Blockgroup":
                self.res_prefix = "bg"
            self.stateCode = self.project.stateCode[self.project.state]
            resultfilename = self.res_prefix+self.stateCode+"_selected"
            #self.resultsloc = self.project.location + os.path.sep + self.project.name + os.path.sep + "results"

            self.resultsloc = os.path.join('%s'%self.project.location, '%s'%self.project.name, "results")

            #self.resultfileloc = os.path.realpath(self.resultsloc+os.path.sep+resultfilename+".shp")
            self.resultfileloc = os.path.join('%s'%self.resultsloc, "%s.shp"%resultfilename)
             

            scenarioDatabase = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)
            self.projectDBC = createDBC(self.project.db, scenarioDatabase)
            self.projectDBC.dbc.open()
            self.makeComboBox()
            self.makeMapWidget()
            self.vbox.addWidget(self.geocombobox)
            self.vbox.addWidget(self.mapwidget)
            self.vboxwidget = QWidget()
            self.vboxwidget.setLayout(self.vbox)
            vbox2 = QVBoxLayout()
            self.vboxwidget2 = QWidget()
            self.vboxwidget2.setLayout(vbox2)
            self.labelwidget = QWidget()
            labellayout = QGridLayout(None)
            self.labelwidget.setLayout(labellayout)
            labellayout.addWidget(QLabel("Selected Geography: " ),1,1)
            labellayout.addWidget(QLabel("Average Absolute Relative Error(AARD): " ),2,1)
            labellayout.addWidget(QLabel("p-value: "),3,1)
            self.aardval = QLabel("")
            self.pval = QLabel("")
            self.selgeog = QLabel("")
            self.aardval.setAlignment(Qt.AlignLeft)
            self.pval.setAlignment(Qt.AlignLeft)
            self.selgeog.setAlignment(Qt.AlignLeft)
            labellayout.addWidget(self.selgeog ,1,2)
            labellayout.addWidget(self.aardval,2,2)
            labellayout.addWidget(self.pval,3,2)

            vbox2.addWidget(self.labelwidget)
            vbox2.addWidget(self.canvas)

            self.hbox = QHBoxLayout()
            self.hbox.addWidget(self.vboxwidget)
            self.hbox.addWidget(self.vboxwidget2)

            indGeoWarning = QLabel("""<font color = blue>Note: Select a geography to show the  performance statistics and display a"""
                                   """ scatter plot showing the comparison between the person weighted sum and the """
                                   """composite person type constraints. </font>""")
            indGeoWarning.setWordWrap(True)
            self.vbox1 = QVBoxLayout()
            self.vbox1.addLayout(self.hbox)
            self.vbox1.addWidget(indGeoWarning)
            self.vbox1.addWidget(self.dialogButtonBox)
            self.setLayout(self.vbox1)

            self.draw_boxselect()
            self.connect(self.geocombobox, SIGNAL("currSelChanged"), self.draw_boxselect)
            self.connect(self.toolbar, SIGNAL("currentGeoChanged"), self.draw_mapselect)

            self.selcounty = "0"
            self.seltract = "0"
            self.selblkgroup = "0"
            self.pumano = -1
        else:
            if check == 1:
                QMessageBox.warning(self, "Results", "Individual Geography Statistics not available for TAZ resolution.", QMessageBox.Ok)
            elif check == 2:
                QMessageBox.warning(self, "Results", "Valid shape file for geography not found.", QMessageBox.Ok)
            elif check == 3:
                QMessageBox.warning(self, "Results", "Run the synthesizer before viewing results.", QMessageBox.Ok)

    def isValid(self):
        retval = -1
        if not self.isResolutionValid():
            retval = 1
            return retval
        elif not self.isLayerValid():
            retval = 2
            return retval
        elif not self.isPopSyn():
            retval = 3
            return retval
        else:
            return retval

    def isResolutionValid(self):
        return self.project.resolution != "TAZ"

    def isLayerValid(self):
        res = ResultsGen(self.project)
        return res.create_hhmap()

    def isPopSyn(self):
        self.getGeographies()
        return len(self.geolist)>0

    def accept(self):
        self.projectDBC.dbc.close()
        self.mapcanvas.clear()
        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        self.mapcanvas.clear()
        QDialog.reject(self)

    def draw_boxselect(self):
        currgeo = (self.geocombobox.getCurrentText()).split(',')

        provider = self.layer.dataProvider()
        allAttrs = provider.attributeIndexes()
        #self.layer.select(QgsRect(), True)
        provider.select(allAttrs,QgsRectangle())
        blkgroupidx = provider.fieldNameIndex("BLKGROUP")
        tractidx = provider.fieldNameIndex("TRACT")
        countyidx = provider.fieldNameIndex("COUNTY")

        selfeatid = 0
        feat = QgsFeature()
        while provider.nextFeature(feat):
            attrMap = feat.attributeMap()
            featcounty = attrMap[countyidx].toString().trimmed()
            if self.res_prefix == "co":
                compid = '%s' %int(featcounty)
                baseid = currgeo[1]
                self.selgeog.setText("County - " + currgeo[1])
            elif self.res_prefix == "tr":
                feattract = ('%s'%(attrMap[tractidx].toString().trimmed())).ljust(6,'0')
                compid = '%s' %int(featcounty) + ',' + '%s' %int(feattract)
                baseid = currgeo[1] + ',' + currgeo[2]
                self.selgeog.setText("County - " + currgeo[1] + "; Tract - " + currgeo[2])
            elif self.res_prefix == "bg":
                feattract = ('%s'%(attrMap[tractidx].toString().trimmed())).ljust(6,'0')
                featbg = attrMap[blkgroupidx].toString().trimmed()
                compid = '%s' %int(featcounty) + ',' + '%s' %int(feattract) + ',' + '%s' %int(featbg)
                baseid = currgeo[1] + ',' + currgeo[2] + ',' + currgeo[3]
                self.selgeog.setText("County - " + currgeo[1] + "; Tract - " + currgeo[2] + "; BlockGroup - " + currgeo[3])
            if (compid == baseid):
                selfeatid = feat.id()
                self.layer.setSelectedFeatures([selfeatid])
                boundingBox = self.layer.boundingBoxOfSelected()
                boundingBox.scale(4)
                self.mapcanvas.setExtent(boundingBox)
                self.mapcanvas.refresh()
                break
        self.selcounty = currgeo[1]
        self.seltract = currgeo[2]
        self.selblkgroup =currgeo[3]
        self.draw_stat()

    def draw_mapselect(self, provider=None, selfeat=None ):
        if provider != None:
            blkgroupidx = provider.fieldNameIndex("BLKGROUP")
            tractidx = provider.fieldNameIndex("TRACT")
            countyidx = provider.fieldNameIndex("COUNTY")


            attrMap = selfeat.attributeMap()
            try:
                self.selcounty = attrMap[countyidx].toString().trimmed()
                if blkgroupidx == -1 & tractidx == -1:
                    self.selgeog.setText("County - " + self.selcounty)
                if tractidx != -1:
                    self.seltract = ('%s'%(attrMap[tractidx].toString().trimmed())).ljust(6,'0')
                    if blkgroupidx == -1:
                        self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract)
                    else:
                        self.selblkgroup = attrMap[blkgroupidx].toString().trimmed()
                        self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract + "; BlockGroup - " + self.selblkgroup)

                geog = '%s' %int(self.stateCode) + "," + '%s' %int(self.selcounty) + "," + '%s' %int(self.seltract) + "," + '%s' %int(self.selblkgroup)
                if geog in self.geolist:
                    self.geocombobox.setCurrentText(geog)
                    #self.draw_boxselect()
                else:
                    self.draw_stat()
            except Exception, e:
                print "Exception: %s; Invalid Selection." %e

    def draw_stat(self):
        self.ids = []
        self.act = []
        self.syn = []
        # clear the axes
        self.axes.clear()
        self.axes.grid(True)
        self.axes.set_xlabel("Joint Frequency Distribution from IPF")
        self.axes.set_ylabel("Synthetic Joint Frequency Distribution")
        self.axes.set_xbound(0)
        self.axes.set_ybound(0)
        self.retrieveResults()
        if len(self.ids) > 0:
            scat_plot = self.axes.scatter(self.act, self.syn)
            xlims = scat_plot.axes.set_xlim()
            ylims = scat_plot.axes.set_ylim()
            maxlim = max(xlims[1], ylims[1])
            scat_plot.axes.set_xlim(0,maxlim)
            scat_plot.axes.set_ylim(0,maxlim)
            xlin = [0,maxlim]
            ylin = [0,maxlim]
            lin = matplotlib.lines.Line2D(xlin,ylin, color='r')
            scat_plot.axes.add_line(lin)
            
        else:
            pass
        self.canvas.draw()


    def on_draw(self, provider=None, selfeat=None ):
        if provider != None:
            blkgroupidx = provider.fieldNameIndex("BLKGROUP")
            tractidx = provider.fieldNameIndex("TRACT")
            countyidx = provider.fieldNameIndex("COUNTY")


            attrMap = selfeat.attributeMap()
            try:
                self.selcounty = attrMap[countyidx].toString().trimmed()
                if blkgroupidx == -1 & tractidx == -1:
                    self.selgeog.setText("County - " + self.selcounty)
                if tractidx != -1:
                    self.seltract = ('%s'%(attrMap[tractidx].toString().trimmed())).ljust(6,'0')
                    if blkgroupidx == -1:
                        self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract)
                    else:
                        self.selblkgroup = attrMap[blkgroupidx].toString().trimmed()
                        self.selgeog.setText("County - " + self.selcounty + "; Tract - " + self.seltract + "; BlockGroup - " + self.selblkgroup)

                geog = '%s' %int(self.stateCode) + "," + '%s' %int(self.selcounty) + "," + '%s' %int(self.seltract) + "," + '%s' %int(self.selblkgroup)

                self.ids = []
                self.act = []
                self.syn = []
                # clear the axes
                self.axes.clear()
                self.axes.grid(True)
                self.axes.set_xlabel("Joint Frequency Distribution from IPF")
                self.axes.set_ylabel("Synthetic Joint Frequency Distribution")
                self.axes.set_xbound(0)
                self.axes.set_ybound(0)
                self.retrieveResults()
                if len(self.ids) > 0:
                    scat_plot = self.axes.scatter(self.act, self.syn)
                    scat_plot.axes.set_xbound(0)
                    scat_plot.axes.set_ybound(0)
                else:
                    pass
                self.canvas.draw()
            except Exception, e:
                print "Exception: %s; Invalid Selection." %e

    def makeComboBox(self):
        self.geolist.sort()
        self.geocombobox = LabComboBox("Geography:",self.geolist)
        self.current = self.geocombobox.getCurrentText()

    def makeMapWidget(self):
        self.mapcanvas = QgsMapCanvas()
        self.mapcanvas.setCanvasColor(QColor(255,255,255))
        self.mapcanvas.enableAntiAliasing(True)
        self.mapcanvas.useImageToRender(False)
        print 'RESULTS FILE LOCATION', self.resultfileloc
        self.layer = QgsVectorLayer(self.resultfileloc, "Selgeogs", "ogr")
        if not self.layer.isValid():
            return
        renderer = self.layer.renderer()
        #renderer.setSelectionColor(QColor(255,255,0))
        #symbol = renderer.symbols()[0]
        #symbol.setFillColor(QColor(153,204,0))
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)
        self.mapcanvas.setExtent(self.layer.extent())
        cl = QgsMapCanvasLayer(self.layer)
        layers = [cl]
        self.mapcanvas.setLayerSet(layers)
        self.toolbar = Toolbar(self.mapcanvas, self.layer)
        self.toolbar.hideDragTool()
        maplayout = QVBoxLayout()
        maplayout.addWidget(self.toolbar)
        maplayout.addWidget(self.mapcanvas)
        self.mapwidget = QWidget()
        self.mapwidget.setLayout(maplayout)

    def getPUMA5(self, geo):
        query = QSqlQuery(self.projectDBC.dbc)
        self.projectDBC.dbc.setDatabaseName(self.project.name)
        self.projectDBC.dbc.open()
        if not geo.puma5:
            if self.project.resolution == 'County':
                geo.puma5 = int('99999'+ str(geo.county).rjust(3, '0'))

            elif self.project.resolution == 'Tract':
                if not query.exec_("""select pumano from geocorr where state = %s and county = %s and tract = %s and bg = 1"""
                                   %(geo.state, geo.county, geo.tract)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]
            else:
                if not query.exec_("""select pumano from geocorr where state = %s and county = %s and tract = %s and bg = %s"""
                                   %(geo.state, geo.county, geo.tract, geo.bg)):
                    raise FileError, query.lastError().text()
                while query.next():
                    geo.puma5 = query.value(0).toInt()[0]
        scenarioDatabase = '%s%s%s' %(self.project.name, 'scenario', self.project.scenario)
        self.projectDBC.dbc.setDatabaseName(scenarioDatabase)
        self.projectDBC.dbc.open()
        return geo


    def retrieveResults(self):

        # Get p-values and aard-values from performance statistics
        performancetable = "performance_statistics"
        aardvalvar = "aardvalue"
        pvaluevar = "pvalue"
        vars = aardvalvar + "," + pvaluevar
        filter = ""
        group = ""

        if self.selblkgroup <> "0":
            filter_act = "tract=" + str(self.seltract) + " and " + "bg=" + str(self.selblkgroup)
            filter_syn = "county=" + str(self.selcounty) + " and " +"tract=" + str(self.seltract) + " and " + "bg=" + str(self.selblkgroup)
        elif self.seltract <> "0":
            filter_act = "tract=" + str(self.seltract) + " and " + "bg=0"
            filter_syn = "county=" + str(self.selcounty) + " and " +"tract=" + str(self.seltract) + " and " + "bg=0"
        else:
            filter_act = "tract=0 and bg=0"
            filter_syn = "county=" + str(self.selcounty) + " and tract=0 and bg=0"

        query = self.executeSelectQuery(self.projectDBC.dbc,vars, performancetable, filter_syn, group)
        aardval = 0.0
        pval = 0.0
        if query:
            while query.next():
                aardval = query.value(0).toDouble()[0]
                pval = query.value(1).toDouble()[0]

        self.aardval.setText("%.4f" %aardval)
        self.pval.setText("%.4f" %pval)

        geo = Geography(self.stateCode, int(self.selcounty), int(self.seltract), int(self.selblkgroup))
        geo = self.getPUMA5(geo)

        self.pumano = geo.puma5

        # Get and populate the actual and synthetics unique person type frequencies for the scatter plot
        if int(self.pumano) > 0:
            actualtable = "person_" + str(self.pumano) + "_joint_dist"
            vars = "personuniqueid" + "," + "frequency"
            group = "personuniqueid"
            query = self.executeSelectQuery(self.projectDBC.dbc,vars, actualtable, filter_act, group)
            if query:
                while query.next():
                    id= query.value(0).toInt()[0]
                    freq = query.value(1).toDouble()[0]
                    self.ids.append(id)
                    self.act.append(freq)

            syntable = "person_synthetic_data"
            vars = "personuniqueid" + "," + "sum(frequency)"
            group = "personuniqueid"
            query = self.executeSelectQuery(self.projectDBC.dbc,vars, syntable, filter_syn, group)
            self.syn = [0.0] * len(self.act)
            if query:
                while query.next():
                    id= query.value(0).toInt()[0]
                    freq = query.value(1).toDouble()[0]
                    if id in self.ids:
                        idx = self.ids.index(id)
                        self.syn[idx] = freq



def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

