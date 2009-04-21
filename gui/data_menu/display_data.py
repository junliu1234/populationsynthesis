from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

from misc.widgets import RecodeDialog
from file_menu.newproject import DBInfo
from database.createDBConnection import createDBC
from misc.widgets import *
from misc.errors import *

class DisplayTable(QDialog):
    def __init__(self, project, tablename, parent=None):
        super(DisplayTable, self).__init__(parent)

        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.filename)
        self.projectDBC.dbc.open()

        self.tablename = tablename

        self.setWindowTitle("Data Table - %s" %self.tablename)


        self.variableTypeDictionary = {}

        self.populateVariableDictionary()

        self.model = QSqlTableModel()
        self.model.setTable(self.tablename)
        self.model.select()

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setMinimumSize(QSize(800, 500))
        self.output = QTextEdit()
        self.output.setMinimumSize(QSize(800, 100))

        layoutView = QVBoxLayout()
        layoutView.addWidget(self.view)
        layoutView.addWidget(self.output)

        descButton = QPushButton("Decriptives")
        freqButton = QPushButton("Frequencies")

        layoutButton = QVBoxLayout()
        layoutButton.addWidget(descButton)
        layoutButton.addWidget(freqButton)
        layoutButton.addItem(QSpacerItem(10, 550))

        hLayout = QHBoxLayout()
        hLayout.addLayout(layoutView)
        hLayout.addLayout(layoutButton)



        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel| QDialogButtonBox.Ok)

        vLayout = QVBoxLayout()
        vLayout.addLayout(hLayout)
        vLayout.addWidget(buttonBox)

        self.setLayout(vLayout)

        self.connect(buttonBox, SIGNAL("accepted()"), self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"), self, SLOT("reject()"))
        
        self.connect(descButton, SIGNAL("clicked()"), self.descriptives)
        self.connect(freqButton, SIGNAL("clicked()"), self.frequencies)

        
    def descriptives(self):
        descriptivesVarDialog = VariableSelectionDialog(self.variableTypeDictionary, 
                                                        title = "Descriptives")
        if descriptivesVarDialog.exec_():
            self.descriptivesVariablesSelected = descriptivesVarDialog.selectedVariableListWidget.variables
            

            COUNT, AVERAGE, MINIMUM, MAXIMUM, SUM = range(5)
            
            query = QSqlQuery()

            self.output.append("DESCRIPTIVES:")
            self.output.append("%s, %s, %s, %s, %s, %s" %('FIELD', 'COUNT', 'AVERAGE', 'MINIMUM', 'MAXIMUM', 'SUM'))

            for i in self.descriptivesVariablesSelected:

                if not query.exec_("""select count(%s), avg(%s), min(%s), max(%s), sum(%s) from %s"""
                               %(i, i, i, i, i, self.tablename)):
                    raise FileError, query.lastError().text()
                while query.next():
                    count = query.value(COUNT).toInt()[0]
                    average = query.value(AVERAGE).toDouble()[0]
                    minimum = query.value(MINIMUM).toInt()[0]
                    maximum = query.value(MAXIMUM).toInt()[0]
                    sum = query.value(SUM).toInt()[0]
                self.output.append("%s, %s, %.4f, %s, %s, %s" %(i, count, average, minimum, maximum, sum))
            self.output.append("")
            
    
    def frequencies(self):
        frequenciesVarDialog = VariableSelectionDialog(self.variableTypeDictionary, 
                                                        title = "Frequencies")
        if frequenciesVarDialog.exec_():
            self.frequenciesVariablesSelected = frequenciesVarDialog.selectedVariableListWidget.variables

            CATEGORY, FREQUENCY = range(2)
            
            query = QSqlQuery()

            self.output.append("FREQUENCIES:")

            for i in self.frequenciesVariablesSelected:
                self.output.append("Variable Name - %s" %i)
                self.output.append("%s, %s" %('CATEGORY', 'FREQUENCY'))
            
                if not query.exec_("""select %s, count(*) from %s group by %s"""
                               %(i, self.tablename, i)):
                    raise FileError, query.lastError().text()
                while query.next():
                    category = query.value(CATEGORY).toString()
                    frequency = query.value(FREQUENCY).toInt()[0]
                    self.output.append("%s, %s" %(category, frequency))
                self.output.append("The %s variable has a total of %s categories" %(i, query.size()))
                self.output.append("")
            
    
    def populateVariableDictionary(self):
        query = QSqlQuery()
        query.exec_("""desc %s""" %self.tablename)

        FIELD, TYPE, NULL, KEY, DEFAULT, EXTRA = range(6)

        while query.next():
            field = query.value(FIELD).toString()
            type = query.value(TYPE).toString()
            null = query.value(NULL).toString()
            key = query.value(KEY).toString()
            default = query.value(DEFAULT).toString()
            extra = query.value(EXTRA).toString()
            
            self.variableTypeDictionary['%s' %field] = type


    def accept(self):
        self.projectDBC.dbc.close()
        QDialog.accept(self)

    def reject(self):
        self.projectDBC.dbc.close()
        QDialog.reject(self)
