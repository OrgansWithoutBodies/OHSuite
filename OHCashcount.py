__version__= '0.0.3'
"""
Created on Tue Aug 21 21:54:53 2018

@author: V

Notes:
    .0:Started app
    .1:Functional
    .2:bigger buttons for touch
    .3:better sizes, more comments,
TODO:
    Able to count both how much to remove to start day w/ given input amt & how m
    Make able to translate text to spanish
    Make sections clear
    Comment more of code for peace of mind
    HELP MENU
    
"""
#importing tools from other libraries, pretty standard - the only part of the script which imports chunks of code from other files
import pandas as pd #efficient number analysis
import sys #needed to get window to continue running

from PyQt5.QtWidgets import * #GUI (Graphical User Interface) library
from PyQt5 import QtGui, QtCore#Specific parts of PyQt5 for ease of coding
###no more imports below this line###

class cashbox(object):#definition of cashbox & what it contains - amount to start, amount epos says, & amount counted by employee
    def __init__(self,amount=0):
        self.sum=amount
        self.empamt=dict([[i,0]for i in cashunits.keys()])#makes a new editable list with cashunits as keys
        self.setstartingsum()
        self.setepossum()
    def setstartingsum(self,amount=1070.5):#don't quite remember exact $
        self.startingsum=amount
    def setepossum(self,amount=None):
        if amount is not None:#if it's called by a user w/ an actual value instead of just to start the program
            self.epossum=amount
    def recalc(self):
        self.sum=sum(self.empamt.values())-self.startingsum#this is what has been put in throughout the day
    def check(self):#is sum greater or equal to what epos says? if so return True 
        if self.sum>=self.eposamt:
            return True
        else:
            return False
          
            
        
    #Base units/amounts cash comes in, 'def'=if unit is default, 'amt'=value amount,'typ': bill or coin - rn only decides which col it's in...
            #rn security does nothing but it's possible to do smth to notify employee to verify authenticity
            
cashunits={'Penny':{'def':True,'amt':0.01,'typ':'Coin','img':''},
           'Nickel':{'def':True,'amt':0.05,'typ':'Coin','img':''},
           'Dime':{'def':True,'amt':0.10,'typ':'Coin','img':''},
           'Quarter':{'def':True,'amt':0.25,'typ':'Coin','img':''},
           'Half Dollar':{'def':False,'amt':0.50,'typ':'Coin','img':''},
           '1 Dollar':{'def':True,'amt':1,'typ':'Bill','img':''},
           '2 Dollar':{'def':False,'amt':2,'typ':'Bill','img':''},
           '5 Dollar':{'def':True,'amt':5,'typ':'Bill','img':''},
           '10 Dollar':{'def':True,'amt':10,'typ':'Bill','img':''},
           '20 Dollar':{'def':True,'amt':20,'typ':'Bill','img':''},
           '50 Dollar':{'def':True,'amt':50,'typ':'Bill','img':'','security':True},
           '100 Dollar':{'def':True,'amt':100,'typ':'Bill','img':'','security':True}}

pcash=pd.DataFrame(cashunits)
##############
class CashWindow(QMainWindow):#main window of actual interface person interacts with - everything above is backend
    def __init__(self): #init header
        super(CashWindow,self).__init__()#makes it so default QMainWindow stuff gets activated
        self.cashbox=cashbox()
        self.sum=0
        self.wind=QWidget()#Empty widget which serves as basis for layout, dumb but only way i've found to get menu bar not to mess up
        self.setCentralWidget(self.wind)
        self.Window()
        self.show() #shows window
        
    def Window(self):#all of what's shown is defined here
        layout = QGridLayout() #Can lay things out in a defined x/y coordinate space
        self.wind.setLayout(layout)
        
        menu=QMenuBar()#if there needs to be file/edit stuff in the future
        self.setMenuBar(menu)
        
        #each individual cash unit
        self.units=dict()
        bj,cj=0,0
        for i in cashunits.keys():
            
            if cashunits[i]['def']:#show only if default - will b editable
                
                if cashunits[i]['typ']=='Bill':
                    j=1
                    jj=bj#janky but works
                    bj=bj+1
                else:
                    j=2
                    jj=cj
                    cj=cj+1
                self.units[i]=unit(i)
                layout.addWidget(self.units[i],jj,j)
                self.units[i].numchanged.connect(lambda ii,i=i:self.recalcsum(i,ii))
                jj=jj+1
        #total
        self.values=dict([[i,0] for i in self.units.keys()])
        self.totaltext='TOTAL $:'
        self.total=QDoubleSpinBox(prefix=self.totaltext,readOnly=True,maximum=100000)
        layout.addWidget(self.total,4,2,2,2)
        self.total.setMinimumHeight(100)
        self.total.setObjectName('total')
        self.total.setButtonSymbols(2)#no updown buttons
        
        etext=QLabel(text='ePos says cash total should be')
        self.epos=QDoubleSpinBox(prefix='epos $:',maximum=100000)
        self.epos.setSingleStep(0.01)
        layout.addWidget(self.epos,2,0)
        layout.addWidget(etext,1,0)
        
        stext=QLabel(text='cash to start each day is:')
        samt=107.5
        self.strt=QDoubleSpinBox(prefix='start $:',maximum=100000)
        self.strt.setReadOnly(True)
        self.strt.setButtonSymbols(2)
        self.strt.setValue(samt)
        
        
        layout.addWidget(self.strt,4,0)
        layout.addWidget(stext,3,0)
        
    def recalcsum(self,unit,num=None):
#        print(unit,num)
        if num is None:
            self.values[unit]=float(self.units[unit].num)
        else:
            self.values[unit]=float(num)
#        print(self.values)
        tsum=sum([self.values[i]*pcash[i]['amt'] for i in self.values.keys()])
        self.total.setValue(tsum)
#        self.total.setMinimumHeight(300)
        self.checksum()
    def checksum(self):
        if self.total.value()>0 and self.epos.value()>0:
            if (self.total.value()-self.strt.value())>=self.epos.value():
                sheet="background-color: green;color:white; "
            
            else:
                sheet="background-color: red; color:black"
        else:
            sheet="background-color: white;color:black;"
        
        self.total.setStyleSheet(sheet)
        
class unit(QGroupBox):#base class which will be duplicated for each cash amount widget
    
    numchanged=QtCore.pyqtSignal(int)
    def __init__(self,amount):
        super(unit,self).__init__()
        self.box=QGroupBox()
        self.bbox=QGroupBox()
        self.bbox.setLayout(QVBoxLayout())
        self.setLayout(QHBoxLayout())
        w=80
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.layout().addWidget(self.bbox)
        unitheight=30
        self.arrs=[QPushButton(text='+',maximumWidth=w,minimumHeight=unitheight),QPushButton(text='-',maximumWidth=w,minimumHeight=unitheight)]
        self.bbox.layout().addWidget(self.arrs[0],0,QtCore.Qt.AlignCenter)
        self.arrs[0].clicked.connect(lambda:self.numinp.setValue(self.numinp.value()+1))
        self.arrs[1].clicked.connect(lambda:self.numinp.setValue(self.numinp.value()-1))
        self.layout().addWidget(self.box,1)
        self.bbox.layout().addWidget(self.arrs[1],1,QtCore.Qt.AlignCenter)
        self.setTitle(amount)
        self.str=amount#string amount
        self.val=cashunits[amount]['amt']#numerical amount this unit is worth
        self.num=0#num is better # to keep as base than $ amt
        self.box.setLayout(QHBoxLayout())
        self.cashinp=QDoubleSpinBox(prefix='$',maximum=10000,minimumHeight=50)
#        self.cashinp.focusChanged.connect(self.cashinp.selectAll)
        self.cashinp.setSingleStep(self.val)
        self.arrs[0]
        
        self.cashinp.setButtonSymbols(0)#sets symbols to +/-
#        self.cashinp.setValidator(QtGui.QDoubleValidator(bottom=0))
        self.cashinp.valueChanged.connect(lambda:self.updateunit('cash'))
        self.box.layout().addWidget(self.cashinp)
        self.numinp=QSpinBox(prefix='num: ',maximum=1000,minimumHeight=50)
        self.numinp.setSingleStep(1)
#        self.numinp.setValidator(QtGui.or(bottom=0))
        self.numinp.valueChanged.connect(lambda:self.updateunit('num'))
        self.box.layout().addWidget(self.numinp)
        self.img=''
#        print('test')
  
        
    @QtCore.pyqtSlot()#makes it editable on input outside 
    def updateunit(self,fromslot):#Ties inputs together
        if fromslot=='cash' or fromslot=='both':#make sure divisible right
            cash=float(self.cashinp.value())
            
            if cash!='':
                self.num=int(cash/self.val)
                self.numinp.setValue(self.num)
        elif fromslot=='num' or fromslot=='both':
           num=self.numinp.value()
           if num!='' :#takes off floating spacebars
    #            if valid:
               self.num=num
               self.cashinp.setValue(round(float(num)*float(self.val),3))
           else:
               self.cashinp.clear()
    
        self.numchanged.emit(self.num)
            
            
def cashrun():
    app=0         
    #windthread=QtCore.QThread()
    
    app=QApplication(sys.argv)
    wind=CashWindow()
    app.exec_()
  
