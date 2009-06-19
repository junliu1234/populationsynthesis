from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from coreplot import *

class Pval(Matplot):
    def __init__(self, project, parent=None):
        Matplot.__init__(self)
        self.project = project
        self.valid = False
        if self.isValid():
            self.valid = True
            self.setWindowTitle("P Value Distribution")
            self.setWindowIcon(QIcon("./images/region.png"))
            pvalWarning = QLabel("""<font color = blue>The above chart shows the distribution of the """
                                 """P-value across all the geographies for which synthetic population was generated."""
                                 """ The p-value gives the probability with which the chosen synthetic population matches the """
                                 """ composite person type constraints. </font>""")
            pvalWarning.setWordWrap(True)
            self.vbox.addWidget(self.canvas)
            self.vbox.addWidget(pvalWarning)
            self.vbox.addWidget(self.dialogButtonBox)
            self.setLayout(self.vbox)
            self.on_draw()
        else:
            QMessageBox.warning(self, "Results", "A table with name - performance_statistics does not exist.", QMessageBox.Ok)
       
    def isValid(self):
        return self.checkIfTableExists("performance_statistics")

    def on_draw(self):
        """ Redraws the figure
        """
        self.err = []
        if self.retrieveResults():
        
            # clear the axes and redraw the plot anew
            self.axes.clear()        
            self.axes.grid(True)
        
            #self.axes.hist(err, range=(1,10), normed=True, cumulative=False, histtype='bar', align='mid', orientation='vertical', log=False)
            self.axes.hist(self.err, normed=False, align='mid')
            self.axes.set_xlabel("P Values")
            self.axes.set_ylabel("Frequency")
            self.axes.set_xbound(None,1)
            self.canvas.draw()      

    def retrieveResults(self):
        projectDBC = createDBC(self.project.db, self.project.name)
        projectDBC.dbc.open()
        
        # Get p-values from performance statistics
        performancetable = "performance_statistics"
        pvaluevar = "pvalue"
        filter = ""
        group = ""
        query = self.executeSelectQuery(projectDBC.dbc,pvaluevar, performancetable, filter, group)
        
        if query:
            while query.next():
                pval = query.value(0).toDouble()[0]
                self.err.append(pval)
            projectDBC.dbc.close()
            return True
        else:
            projectDBC.dbc.close()
            return False
        
        
def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
#    res.show()
#    app.exec_()
    QgsApplication.exitQgis()

if __name__ == "__main__":
    main()

