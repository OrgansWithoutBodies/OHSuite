__version__='0.2.8'
"""
0.2.4 notes - fixed categories in stats window
A: fixed offset bug in graphs, made csv export work, introduced more bugs :/
B: Fixed some of said bugs, implemented some threading on statwindow
C: fixed function-impairing bugs! still hangs on load of statswindow

0.2.5 - threading for statswindow works! :)
A - Started implementation of email,e still not entirely sure how it's gonna work. Some Gui Cleanup & Code class reshufflings

0.2.6 - updated receipts
A - implement Dump Fee
B - updated catmap - write to renew, fixed old receipts bug, switched logo

0.2.7 - email working, made complaint text bigger 

0.2.8 - "Close Dock Early" btn - buggy on redirect? 



TODO
    EMAIL
    Scheduled info graph 
    migrate graph to bokeh?
    IMPORT DONATIONS FROM LOG
    Have Company name be acceptable for inputs
    Make completer understand donor less jankier (flexible-r order - custom model)
    more ways to accept w completer 
    make categories/catmap editable
    animation/some vis feedback that things print/save
    more try/excepts to b safer
    old receipts able to view by date, sortable
    Dump Fee Vertical Orientation when small enough
    make things look nicer
    get categories from db/default to some if no conn
    make menu actions
    name label remover?
    Make Receipt formatter?
"""
import sys 
import importlib
import datetime
import math
import pandas
import webbrowser
import functools
import sqlite3
import logging
import os
import threading
import win32api
import win32ui
import win32print
import numpy as np 
import subprocess
import pythoncom
import OHMailer 
import requests
import json
#import apscheduler

#import datetime
#import sqlcipher #for encrypted database

from PyQt5 import QtGui, QtCore,QtSql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QPainter, QPolygon

from OHLib import *
from PIL import ImageQt, Image, ImageDraw, ImageFont,ImageOps,ImageWin

from pandas import DataFrame as DF
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as mp

from win32com.taskscheduler import taskscheduler
#QMainWindow,QApplication,QPushButton


JoinRole = QtCore.Qt.UserRole +1


"""QT GUI Making Below Here


"""

class Threader(QtCore.QThread):
    def __init__(self,fn=None,parent=None):
        super(Threader,self).__init__()
        self.parent=parent
        if fn!=None:
            self.fn=fn
            self.run()
        
    def run(self):
        fn(parent)
    

class DonationWindow(QMainWindow):
    def __init__(self): #init header
        
        super(DonationWindow,self).__init__()
        def windowRun():
            
            self.winds=dict()
            
            self.experimental=curdoc.split('\\')[-1]==expdict[False]['file']+'.py'
        
            self.wind=QWidget()
            self.setCentralWidget(self.wind)
            stylesheet="""
            QGroupBox { font-weight: bold; font-size: 30px;} 
            """
            cols=['red','yellow','green','blue','purple']
            for c in range(len(cols)): #a lot easier than manually doing each one, make sure names don't change
                stylesheet=stylesheet+'QPushButton#'+str(c)+':checked{background-color:'+cols[c]+'; font-size:15px} '
            self.setStyleSheet(stylesheet)
            
            self.renderthread=QtCore.QThread()
            self.renderthread.run=self.printthrd
            self.renderthread.finished.connect(lambda:self.savefn(pr=1))
            
            
            self.Window()
            #self.AddCustWindow()
            # set my layout to make sure contents are correctly rendered
            
        self.windowThread=QtCore.QThread()
        self.windowThread.run=windowRun()
        #check if anything in Q here
        
        self.mailThread=QtCore.QThread()
#        self.mailThread.run=pass
        
    def showwind(self,wind,thread=False):
        if thread==True:#loads window in a thread, then shows
            self.bar=QProgressBar()
            self.loadwindthread=QtCore.QThread()
            self.loadwindthread.run=wind()
            #print('test')
#            self.bar.show()
            self.loadwindthread.start()
            
            self.loadwindthread.finished.connect(lambda:self.winds[wind].show())
        else:
            self.winds[wind]=wind()
            self.winds[wind].show()
    def Window(self):
        #Menus
        
        self.dumpfee=0
        layout = QGridLayout() # create layout 
        layoutwidg=QWidget()
        layoutwidg.setLayout(layout)
        superlayout=QHBoxLayout()
        superlayout.addWidget(layoutwidg)
        self.wind.setLayout(superlayout)
        menu=QMenuBar()
        self.setMenuBar(menu)
#       
        helpMenu=menu.addMenu('Help')
        
        link=helpMenu.addAction('Bugs/Feedback/Tutorial (functional)')
        link.triggered.connect(lambda:webbrowser.open_new(feedbacklink))
        
        
        custMenu=menu.addMenu('Donors')
        newdon=QAction(text="Add New Donor (tbd)")
        newdon.setMenuRole(1)
        custMenu.addAction(newdon)
        newdon.triggered.connect(self.NewCust)
        #custMenu.addAction('Browse Donors (tbd)')
        
    
        self.closeDockEarlyBtn=QPushButton('Close \nDock \nEarly'.upper())
        self.closeDockEarlyBtn.setMaximumSize(80,80)
        earlylayout=QVBoxLayout()
        earlylayout.addWidget(self.closeDockEarlyBtn)
        earlylayout.addStretch(2)
        closewidg=QWidget()
        closewidg.setLayout(earlylayout)
        superlayout.addWidget(closewidg)    
        
        self.closeDockEarlyBtn.clicked.connect(lambda:self.showwind(wind=CloseDockEarlyWindow))

        oldrec=custMenu.addAction('Reprint Old Receipts (mostly functional)')
        oldrec.triggered.connect(lambda: self.showwind(wind=OldReceiptWindow))
        
        donMenu=menu.addMenu('Donations')
        stats=donMenu.addAction('Donation Statistics (mostly functional)')
        stats.triggered.connect(lambda: self.showwind(wind=StatsWindow))
        
       #maybe not workable/worth the effort
#        def expfn():
#            print(expdict[self.experimental]['file'])
#            subprocess.call(" python ")
#            s=importlib.util.spec_from_file_location("dockrun",wd+r"\\"+expdict[self.experimental]['file']+'.py')
#            f=importlib.util.module_from_spec(s)
#            s.loader.exec_module(f)
#            f.dockrun()
        
        fileMenu=menu.addMenu('File')
#        expmode=fileMenu.addAction('Change to %s version'%expdict[self.experimental]['str'])
#        expmode.triggered.connect(expfn)
        fileMenu.addAction('Relocate Database (tbd)')
        
        customMenu=fileMenu.addMenu('Customize')
        langMenu=fileMenu.addMenu('Change Language/cambiar idioma (tbd)')
        customMenu.addAction('Change Color Scheme (tbd)')
        customMenu.addAction('Customize Receipt Format (tbd)')
        
        
        #App 
        cats=["Books","Furniture","Electronics","Household","Kitchen","Clothes","Toys","Misc."] #flexible inputs of what items to donate
        helplayout=QHBoxLayout()
        layout.addLayout(helplayout,10,1,alignment=QtCore.Qt.AlignRight)
        helpbutton=QPushButton()
        helpbutton.setCursor(QtCore.Qt.PointingHandCursor)
        hs=40
        helpbutton.setFixedSize(hs,hs)
        helpbutton.setStyleSheet("""border-image: url(Visuals/Questionbuttonsmall.png) 1 5 5 5;
""")
        helplayout.addWidget(QLabel("Help,Complaints,or Opinions Here ->",font=QtGui.QFont('Helvetica',12)))
        
        helplayout.addWidget(helpbutton)
        helpbutton.clicked.connect(lambda:webbrowser.open_new(feedbacklink))
        #cats={'270.0','271.0','272.0','273.0','274.0','275.0','276.0','277.0','278.0','279.0','280.0','281.0','282.0','284.0','293.0'}
        self.don=Donation() #this new donation object
        
        pclayout = QGridLayout()
       
        #make add new user a modal window
        
        vrslbl=QLabel(text='<i>'+'version: '+__version__+'</i>',textFormat=1)
        layout.addWidget(vrslbl,10,1)
        self.inp=QLineEdit()
        self.inp.setPlaceholderText("Insert Existing Donor Name Here") #compare sets split at comma
        nm=self.inp.text()
        pclayout.addWidget(self.inp,0,0)
       # inp.textChanged.connyect(self.lookupname)
        global db
        db=QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName(dbpath)
        db.open()
       
        self.query=QtSql.QSqlQuery(db)
        self.query.exec("SELECT Firstname, Lastname,id FROM Donors")
       
        self.modl=QtSql.QSqlTableModel() #Base model where customer names come from, has two columns
        self.modl.setQuery(self.query)
        
        
        self.modl.setTable("Donors")
        self.modl.select()
        while self.modl.canFetchMore():
            self.modl.fetchMore()
        db.close()
        modl=self.modl #temp cleanup fix
        
        cols=[1,2]
        self.proxy=nameLookupModel(columns=cols)
        proxy=self.proxy
        
        #self.proxy.setFilterColumns=[0,1,2]
        self.proxy.setSourceModel(modl)#sql model gets fed into proxy, which takes strings 
        #self.inp.editingFinished.connect(proxy.setFilterFixedString)
        #print(self.proxy.data(self.proxy.index(0,2)))
        #proxy.setFilterRegExp()
        
         
        self.complete=CustomQCompleter(self,proxy=proxy,columns=cols)
        def selectdonorfn(ind): #given an index, makes donor into selected one
            donrec=self.modl.record(ind.data())
            indt={}
            for i in FL:
                indt[i]=donrec.field(i+'name').value()
            
           
            self.don.updateDonor(indt)
            self.nmlbl.update(self.don.donor)
            
        self.complete.activated[QtCore.QModelIndex].connect(lambda index: selectdonorfn(index)) #do something here to include index?
#        self.complete.setCompletionColumn(2)
#        self.complete.setModel(self.proxy)
        
        self.inp.setCompleter(self.complete)
        self.inp.setClearButtonEnabled(True)
        
        class nmlbl(QWidget):
            def __init__(self,donor=None):
                super(nmlbl,self).__init__()
                self.lbl=QLabel(textFormat=1,alignment=QtCore.Qt.AlignRight) 
                self.lbf=QtGui.QFont('Helvetica',12)
                self.lbl.setFont(self.lbf)
                l=QGridLayout()
                l.addWidget(self.lbl)
                self.setLayout(l)
                if donor!=None:
                    self.update(donor)
            def update(self,donor):
                if donor.stringName!='none none':
                    self.lbl.setText(donor.stringName+' donated:')
                else:
                    self.lbl.clear()
        self.nmlbl=nmlbl()
        
        pclayout.addWidget(self.nmlbl,2,0)
#        pclayout.setColumnStretch(1,1)
#        pclayout.setColumnStretch(2,1)
        #complete.setModel(modl)
        pcwidg=QWidget()
        pcwidg.setLayout(pclayout)
        newcust=QPushButton("Add New Donor into system")
        newcust.setMinimumSize(200,50)
        pclayout.addWidget(newcust,1,0)
        
        newcust.setFont(QtGui.QFont('Arial',9,weight=63))
        
        
        newcust.clicked.connect(lambda: self.NewCust(self))
       
        unitlayout=QGridLayout()
#        layout.addLayout(pclayout,0,0)
#        layout.addLayout(unitlayout,0,1)
        laywidg=QWidget()
        laywidg.setLayout(unitlayout)
        split=QSplitter()
        split.setChildrenCollapsible(False)
        split.setOpaqueResize(False)
        split.setHandleWidth(5)
        split.addWidget(pcwidg)
        split.addWidget(laywidg)
        split.setStyleSheet("""QSplitter::handle {
   background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 2px solid #777;
width: 13px;
margin-top: 2px;
margin-bottom: 2px;
border-radius: 4px;}""")
        layout.addWidget(split,1,1)
        
        
        self.units=dict()
        gridsize=(4,2)#rows,cols
        for i in cats: #do smth to make this wrap around like a grid
            self.units[i]=self.DonationUnit(i,self.don) #cats encodes list order implicitly
            row=cats.index(i)%gridsize[0]
            col=2*math.floor(cats.index(i)/gridsize[0])
            unitlayout.addWidget(self.units[i].box,row,col,1,2)
        svs=QGroupBox()
        svlay=QVBoxLayout()
        svs.setLayout(svlay)
        svsss='font-size: 20px'
        
        
        dumpfeebox=QGroupBox(title='Dump Fee',alignment=QtCore.Qt.AlignCenter)
        dumpfeebox.setObjectName('Dump')
#        dumpfeebox.setCheckable(True)
#        dumpfeebox.setChecked(False)
        dumpfeebox.setStyleSheet('QPushButton#Small:checked{background-color:lime;} QPushButton#Large:checked{background-color:darkGreen;color:white;}QGroupBox#Dump{font-size:12px}')
        pclayout.addWidget(dumpfeebox,3,0)
#        pclayout.setColumnStretch(2,1)
        pclayout.setRowStretch(2,1)
        pclayout.setRowStretch(4,2)
        dumpdicts={'No':0,'Small':20,'Large':40}
#        self.
        dumplay=QHBoxLayout()
        self.dumpbutts=QButtonGroup(dumpfeebox)
        dumpbutts=self.dumpbutts
#        dumpbutts.setOrientation(QtCore.Qt.Horizontal)
#        dumpbutts.se1tChe
        for i in dumpdicts.keys():
            ii=dumpdicts[i]
            butt=QPushButton(dumpfeebox)
            butt.setCheckable(True)
#            butt.setAutoExclusive(True)
            butt.setObjectName(i)
            if i=='No':
                butt.setChecked(True)
                dtext=''
            else:
                butt.setChecked(False)
                dtext='\n($'+str(ii)+")"
            butt.setText(i+' Fee'+dtext)
            dumpbutts.addButton(butt,id=ii)
            dumplay.addWidget(butt)
        dumpbutts.setExclusive(True)
        
        def dumpfn():
            q=self.dumpbutts.checkedId()
            self.don.updateQuant('Dump Fee',q)
            print(self.don.items)
        dumpbutts.buttonClicked.connect(dumpfn)
        dumpfeebox.setLayout(dumplay)
        
        
        pclayout.addWidget(svs,5,0,2,1)
        
        pclayout.setRowStretch(7,3)
        prsz=(200,50)
        rec=QPushButton('Save && &Print Receipt')
        rec.setMinimumSize(*prsz)
        rec.setStyleSheet(svsss)
        rec.clicked.connect(self.renderthread.start)
        svlay.addWidget(rec)
        
        
        sv=QPushButton('Save without printing')
        sv.setMinimumSize(*prsz)
        sv.setStyleSheet(svsss)
        sv.clicked.connect(self.savefn)
        svlay.addWidget(sv)
        
        self.setGeometry(50,50,500,300)
        self.setWindowTitle("Donations Application")
        
        self.show()
    def clearpg(self):  
        self.don=Donation()
        self.dumpbutts.button(0).setChecked(True)
        self.inp.clear()
        for u in self.units.keys():
            self.units[u].btns[0].setChecked(True)
            self.units[u].resetdon(self.don)
            self.units[u].cst.setText('')
        self.nmlbl.update(self.don.donor)
    def addtothread(self,fn):
        def run(fn):
            Threader(fn,self)
        run(fn)
    #@addtothread
    
    def printthrd(self):#need to include this before savefn? so it can check if input is valid
        #print(self.don.items)
        self.r=Receipt([self.don])
        

        self.x=self.r.render()
        
    def savefn(self,pr=0):
        #need to check if there are items and donor
       
        donor=self.don.donor
        nminv=donor.name["First"] is None and donor.name["Last"] is None
        doninv=len(self.don.items)==0
        #print(self.don)
        #print(nminv,doninv)
        if nminv or doninv:
            QMessageBox(text='Invalid entry!',informativeText="Missing input for "+', '.join((('Name' if nminv==True else ''),('Donation' if doninv==True else '')))).exec()
        else:
            a=donor.isindb()
         #   print(a)
#            if not a:  #maybe save from somewhere else (addcustwind signal)? so that it won't have to requery each time
#                #dnrsv=donor.saveDonor()
#                if dnrsv==True:
#                    print("saved donor!")
#                else:
#                    print('donor whoops!')
                #connwrite(path+dbname,("INSERT INTO Donors (Firstname, Lastname) VALUES (?,?)",(dbFilter(donor.name["First"]),dbFilter(donor.name["Last"]))))
#            else: #donor's in db already, so just need to save donation
#                pass
            saved=self.don.saveDonation() 
            if saved==True:
                print('saved donation!')
            else: 
                print('donation whoops!')
            if pr==1:
                filename=wd+r'\test.png'
              #  print(filename)
              
                self.x.save(filename)
                try:
                    expprint(filename)
                except:
                    QMessageBox(text="Printing failed for some reason", informativeText="Donation is saved, but something went wrong between here and the printer").exec()
           #now that that's all done, clear the page
            self.clearpg()    
            

    def NewCust(self,parent):
        global cust #makes window not disappear by autocleanup
        cust=AddCustWindow(parent) #parent is DonationWindow object
        cust.show()    
    class DonationUnit(object): #
        def __init__(self,cat,don,numrow=False):
            self.box=QGroupBox(cat)
            self.don=don
            self.numrow=numrow
            self.cat=cat
            self.box.setAlignment(QtCore.Qt.AlignCenter)
            lbox=QGridLayout()  
            lbox.setVerticalSpacing(1)
            global amtdict
            amtdict={0:"None",1:"One",2:"Some",3:"A Lot", 4:"Too Much"} # receipts will say "x donated [amtdict[x]] of y" or smth
            #have custom amountbox?
            self.btns=dict()
            nf=QtGui.QFont('Helvetica',6)
            for i in amtdict.keys():
                 self.btns[i]=QPushButton(amtdict[i]+" (%i)"%i)
                 
                 btn=self.btns[i]
                 btn.setCheckable(True)
                 btn.setObjectName(str(i))
                 btn.setMinimumSize(80,35)
                 btn.font().setPointSize(15) #not working
                 if i==0: #by default none is selected on all units
                     btn.setChecked(True)
                 btn.setAutoExclusive(True) #makes it one-of-many choice
                 
                 
                 btn.pressed.connect(lambda loc=[cat,i]:self.clickfn(*loc)) #SORTA HACKY OOPS CAPS UNINTENTIONAL BUT RELEVENT
                 lbox.addWidget(btn,0,i) 
                 #lbox.addWidget(QLabel(text='('+str(i)+')',alignment=QtCore.Qt.AlignCenter,font=nf),1,i)
            self.cst=QLineEdit()
            self.cst.setMaximumWidth(50)
            self.cst.editingFinished.connect(self.inputfn)
            
            #do something to check that text is int
            lbox.addWidget(self.cst,0,len(amtdict))
           # lbox.addWidget(QLabel(text='(...)',alignment=QtCore.Qt.AlignCenter,font=nf),1,len(amtdict))
            
            self.box.setLayout(lbox)
        def resetdon(self,don):
            self.don=don
        def clickfn(self,cat,val):#checks 
            if self.cst.text()!='':
                    self.cst.setText('')
            self.don.updateQuant(cat,val)
            if self.btns[val].autoExclusive()==False:#if last input was via edit bigger than buttons, these won't be autoexclusive
                
                for i in self.btns.keys():
                    self.btns[i].setAutoExclusive(True)
                
                    
        def inputfn(self):
            try:
                if self.cst.text().strip()=='':#text stripped of spaces is 
                    amt=0
                else:
                    try:
                        amt=int(float(self.cst.text()))
                    except ValueError: #cst is not a number
                        QMessageBox(text='Please enter a number!').exec()
                        self.cst.clear()
                self.don.updateQuant(self.cat,amt)
                
                if amt in amtdict.keys():
                    self.btns[amt].setChecked(True)
                else: 
                    for i in self.btns.keys():
                        self.btns[i].setAutoExclusive(False) #uncheck all - can't do when exclusive
                        self.btns[i].setChecked(False)
                        self.btns[i].setAutoExclusive(True)
#                        
                        
                    
                    
            except: 
                
                return None

class CloseDockEarlyWindow(QWidget):#threadify
    
    sessionAuthenticated=QtCore.pyqtSignal()
    authenticationFailed=QtCore.pyqtSignal()
    postFailed=QtCore.pyqtSignal()
    postSucceeded=QtCore.pyqtSignal()
    connectionError=QtCore.pyqtSignal()
    #request format: first do GET request to get CSRF cookie, 
    #then POST login info w cookie as data
    #then POST api info w CHANGED cookie (from step 2) in header
    def __init__(self,parent=None):
        super(CloseDockEarlyWindow,self).__init__(parent)
        self.Window()
        
    def authenticate(self,username,password):
        loginuri=self.url+'/api-auth/login/'
        nextstr='?next=/api/dock/'
        csrfkey='csrfmiddlewaretoken'
        try:   
            r=self.S.get(loginuri)#load page first to get token, if fails then likely server is down/firewall or smth is blocking communication
         
            if r.status_code==200:
                csrf=self.S.cookies['csrftoken']    
                try: #if something goes wrong with the connection it doesn't return anything and just hangs, likely something to do with redirection detection :/
                    rr=self.S.post(loginuri+nextstr,data={"username":username,'password':password,csrfkey:csrf},allow_redirects=True)
                except:
                    self.connectionError.emit()
                    raise
                    return False#breaks out of fn
                
                if rr.history: #existence means that has been redirected - if current page is ok & last page was redirect:
                    print(rr.history[0].status_code==302)
                    print(rr.status_code==200)
                    if (rr.status_code ==200 and rr.history[0].status_code ==302):
                        print('test')
                        self.sessionAuthenticated.emit()
                        return True    
                    
                self.authenticationFailed.emit()#rr has no history aka hasn't been redirected - usually means wrong pwd
                return False    
            
            self.connectionError.emit()#r didn't return ok status code so likely site is currently not connectable
            raise
            self.S.close()
            #            return False
        except:
            self.postFailed.emit() #don't necessarily know why failed
            raise
    def closedockfn(self,usr,pwd,reason=None): #constructs data & calls api stuff
    
        timestrcode='%FT%TZ' #strftime format for posting time - [DATE]T[TIME]Z
        timekey="early_closes" #key for dock time slot name
        reskey='reason'
        data={timekey:datetime.datetime.now().strftime(timestrcode)}
        if reason is not None:
            data[reskey]=reason
        print(self.postToAPI(usr,pwd,data=data))
    def postToAPI(self,username='',password='',baseurl='http://localhost:8000',data={}):
        #needs better handling of urls
        baseurl="http://104.248.187.62:8000"
        self.url=baseurl
       # url="http://104.248.187.62"
       
        uri=self.url+"/api/dock/"#better name
        
        otherkey='X-CSRFToken'
        #r.status_code
        self.S=requests.session()
#        MAX_RETRIES = 20
#        adapter = requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES)
#        self.S.mount('http://', adapter)

        try:
            if self.authenticate(username,password):#if authentication returns not False
      
                csrf=self.S.cookies['csrftoken']
                print(data,uri)
                r=self.S.post(uri,data=data,headers={otherkey:csrf,'Referer':uri})
                print(r,csrf,self.S.cookies)
                if r.status_code==201:
                    
                    self.S.close()
                    self.postSucceeded.emit()
                    return True
     
            self.S.close()
            self.postFailed.emit()
            return False #sends an API thingy to website
        except ConnectionError:
            self.S.close()
            self.postFailed.emit()
            return False
        
    def Window(self):
        layout=QGridLayout()
        self.setLayout(layout)
        userfield=QLineEdit(placeholderText="Username")
        passfield=QLineEdit(placeholderText="Password",echoMode=QLineEdit.Password)
        layout.addWidget(userfield,0,0)
        layout.addWidget(passfield,1,0)
        
        reasonfield=QTextEdit(placeholderText="Reason for closing early (optional)",acceptRichText=False)
        layout.addWidget(reasonfield,2,0)
        
        btn=QPushButton(text="Submit")
        btn.clicked.connect(lambda:self.closedockfn(userfield.text(),passfield.text(),reasonfield.toPlainText()))
        layout.addWidget(btn,3,0)
        
        
        
        self.authenticationFailed.connect(lambda:QMessageBox(text='authentication error!').exec())
        self.postFailed.connect(lambda:QMessageBox(text="post couldn't send sorry :/").exec())
        self.postSucceeded.connect(lambda:QMessageBox(text='success!').exec())
        self.connectionError.connect(lambda:QMessageBox(text='Connection Problem, sorry!').exec())
class OldReceiptWindow(QWidget):
    def __init__(self,parent=None):
        #asks for input of donor, then select which donations to reprint
        super(OldReceiptWindow,self).__init__(parent)
        self.Window()
        
        self.setStyleSheet("""QSplitter::handle {
   background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0 #eee, stop:1 #ccc);
border: 2px solid #777;
width: 13px;
margin-top: 2px;
margin-bottom: 2px;
border-radius: 4px;}""")
        
    def Window(self):
        #fns
        def donorselfn():
            qrybase="SELECT * FROM Donations WHERE donorid = "#base string which gets updated based on selection
            sel=self.vw.selectionModel()
            selid=sel.selection().indexes()[0].data()#id of donor selected
            
            qry=qrybase+str(int(selid))
            db.open()
            q=QtSql.QSqlQuery(db)
            q.exec(qry)
            self.donordons.setQuery(q)
            while self.donordons.canFetchMore():
                self.donordons.fetchMore()
            db.close()
        def reprintfn():
            ids=[i.data() for i in self.donvw.selectionModel().selection().indexes()]
            dons=donationParser(ids)
            print(list(dons.values()))
            rec=Receipt(list(dons.values()))
            fn=wd+r'\test.png'
            rec.render().save(fn)
            expprint(fn)
            
        layout=QGridLayout()
        self.setLayout(layout)
        #test=QPushButton('show donations') #make this pop up when donor(s) selected
        #layout.addWidget(test)
        db.open()
        modl=QtSql.QSqlTableModel(db=db)
        modl.setTable("Donors")
        modl.select()
        while modl.canFetchMore():
            modl.fetchMore()
        db.close()
        
       #Views & Models
        self.vw=QTableView()
        self.sel=QtCore.QItemSelectionModel()
        self.vw.setSelectionModel(self.sel)
        self.sel.setModel(modl)
        
        self.vw.setModel(modl)
        self.vw.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vw.setSelectionBehavior(QAbstractItemView.SelectRows) #selects rows
        self.vw.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.vw.selectionModel().selectionChanged.connect(donorselfn)#whenever the selected donor is changed, the donvw is updated w all the donations of that donor
#       
        self.donordons=QtSql.QSqlQueryModel()
        self.donvw=QListView()
        self.donvw.setSelectionMode(QAbstractItemView.MultiSelection)
        self.donvw.setModel(self.donordons)
        
        
        #Buttons & Other Widgets
        self.printbtn=QPushButton('reprint receipt w/ selected') 
        self.printbtn.clicked.connect(reprintfn)
        selbtn=QPushButton('Select all donations')
        
        self.lkup=QLineEdit()
        self.lkup.setPlaceholderText('Lookup Donor Name')
            
       
        split=QSplitter()#split between left right
        
        layout.addWidget(split)
        
        custsplit=QSplitter(QtCore.Qt.Vertical)
        split.addWidget(custsplit)
        custsplit.addWidget(self.lkup)
        custsplit.setChildrenCollapsible(False)
        custsplit.addWidget(self.vw)
        
        printsplit=QSplitter(QtCore.Qt.Vertical)
        split.addWidget(printsplit)
        printsplit.addWidget(self.donvw)
        printsplit.setChildrenCollapsible(False)
        printsplit.addWidget(self.printbtn)
        
        
        
def donationParser(ids):#parses donation from list of ids in db to donation obj
    #can prob do all this sql in one query/2?
    dn=connwrite(dbpath,["SELECT * FROM Donations WHERE id IN ("+','.join([str(i) for i in ids])+')'])
    dnr=connwrite(dbpath,["SELECT * FROM Donors WHERE id=?",(str(dn[0][1]),)])
    sel=connwrite(dbpath,["SELECT * FROM DonationLines WHERE donationid IN ("+','.join([str(i) for i in ids])+')'])
    cats=connwrite(dbpath,["SELECT CategoryMap.id,DonationCategories.name FROM CategoryMap JOIN DonationCategories ON mapstoid=DonationCategories.id WHERE CategoryMap.id IN ("+','.join([str(i[2]) for i in sel])+')'])
    
    quantid=3
    catid=2
    idid=1
    
    
    donlist=dict()
    for d in range(len(ids)): 
        donlist[ids[d]]=Donation(donor={'First':dnr[0][1],'Last':dnr[0][2]},date=dn[d][2])
        print(cats)
        [donlist[ids[d]].updateQuant(quant=l[quantid],item=dict(cats)[l[catid]]) for l in sel if l[idid]==ids[d]]#susceptible to order changing
        print(donlist[ids[d]].items) 
    return donlist

"""
completer takes input from text box, splits it up around comma. 
when comma is typed, make stuff before comma prefix?

"""
  
class CustomQCompleter(QCompleter): #dropdown box of suggestions
    """
    adapted from: http://stackoverflow.com/a/7767999/2156909
    """
    
    def __init__(self, parent=None,model=None,proxy=None,columns=None,*args):#parent=None):
        self.columnind=0
        super(CustomQCompleter, self).__init__(parent,*args)
        
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.parent=parent
        #self.setCompletionColumn(self.columnind)
        #self.popup().setStyleSheet("background-color: yellow")
        #self.popup().setStringList('test')
        # columns: are the columns that are going to concatenate
        if proxy!=None:
            self.setModel(proxy)
        elif model!=None:
            proxy = nameLookupModel(columns)
            proxy.setSourceModel(model)
            self.setModel(proxy)
        
        
        self.setCompletionRole(JoinRole)
        self.setFilterMode(QtCore.Qt.MatchContains)
        
        self.popup().setItemDelegate(JoinDelegate(self))   
        
       # self.filterProxyModel = parent.(self)
       # self.usingOriginalModel = False
#
    def setModel(self, model): #
        self.source_model = model
        
        self.filterProxyModel=model
       # print(model.data) #want to have one column???
        super(CustomQCompleter, self).setModel(self.source_model)
        
       # self.updateModel()
      #  self.usingOriginalModel = True
#    def setPopup(self,View):#nothing happening???
#        print(self) 
#        print(View)
#
#        #super(CustomQCompleter,self).setPopup(self,View)-
#    def updateModel(self):
#        if not self.usingOriginalModel:
#            self.filterProxyModel.setSourceModel(self.source_model)
#   #     class InnerProxyModel(QSortFilterProxyModel):
#        pattern = QtCore.QRegExp(self.local_completion_prefix,F
#                                QtCore.Qt.CaseInsensitive,
#                                QtCore.QRegExp.FixedString)
#
#        self.filterProxyModel.setFilterRegExp(pattern)
        
    def pathFromIndex(self,index,role=QtCore.Qt.DisplayRole): #decides what gets put into selection box
        #print(index)
        model=self.source_model
        return model.data(model.index(index.row(),0),role=JoinRole)
#    def splitPath(self, path):
#        self.local_completion_prefix = path #???
#        #print(path)
#        sp=self.local_completion_prefix.split(',')
##        if len(sp)>1: #
##            print('path split '+sp[0]+sp[1])
##            print(self.source_model)
##            return sp
#
#        return [path]
class JoinDelegate(QStyledItemDelegate):
   
    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = index.data(role=JoinRole)
       
        widget = option.widget
        style = widget.style() if widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)
        #super(JoinDelegate,self).paint(painter, option, index)
class nameLookupModel(QtCore.QIdentityProxyModel): 
    def __init__(self, columns=None,parent=None,base=None):
        super(nameLookupModel, self).__init__(parent)
        self._columns = columns
        #self.filterFunctions = {} 
        #self.filterColumns=[0,1]xane
        self.baseModel=base #not needed?
#    def setSourceModel(self,model):
#        
#        super(nameLookupModel,self).setSourceModel(model)
#        
        #self.data = 
#    def filterAcceptsRow(self, row_num, parent): #input matches if this returns true
#       
#        self.filterString=self.parent().inp.text()
#        self.filterList=[i.strip() for i in self.filterString.split(',')]
#        l=len(self.filterList)
#        while l<2:#easiest way to get thru this atm, clean up later
#            self.filterList.append('')
#            l=len(self.filterList)
#        if self.baseModel is not None:
#            model=self.baseModel
#        else:se
#            model = self.sourceModel()  # the underlying model, 
#       
#                          # implmented as a python array
#        
#        row = [model.data(model.index(row_num,0)),model.data(model.index(row_num,1))] #gets the data for this row from sql model in list format
#        
#        
#        
#        #(row[0] starts with fname and row[1] starts w lname) OR vice versa
#        tests=[row[0].startswith(self.filterList[i]) and row[1].startswith(self.filterList[1-i]) for i in [0,1]]
#        #tests = len(self.filterSet.intersection(set([row[col] for col in self.filterColumns])))==2
#       # print(tests)
#        return True in tests        # accepts row if any column
#                                    # contains filterString
#    def data(self,index,role=QtCore.Qt.DisplayRole):
#        #print(index.column())
#        
#        if index.column()==2:
#            print(index)
#            model=self.sourceModel()
#            row=[model.data(mode.index(index.row(),0)),model.data(model.index(index.row(),1))]
#            
#            return str(row[0])+','+str(row[1])
#        else:
#            return super(nameLookupModel,self).data(index,role)
        
    def data(self, index, role):
        errs=0
        if role == JoinRole: #join role 
            texts = []
            
            if self._columns is not None:
                for c in self._columns:
                    #print(self.sibling(index.row(),c,index.parent()))
                    texts.append(self.sibling(index.row(), c, index.parent()).data())
               # print(", ".join(texts))
                return ", ".join(texts)
               
        return super(nameLookupModel,self).data( index, role)
#    def columnCount(self,index=None):
#        if self.sourceModel() is not None:
#            return self.sourceModel().columnCount()+1
#        return 0#else
#    
#    
    
    
#    

class AddCustWindow(QWidget): #window to add new customer 
    """
    TO DO
    Make searchable
    order by date
    
    """
    def __init__(self,parent=None): #Header init
        super(AddCustWindow,self).__init__()
        neccol='red'
        self.setStyleSheet("""QLineEdit{border: 5px ridge #F3F3F3;font-style:bold;font-size:16px;background-color:#F8F8F8;padding: 0 8px} 
            QLineEdit#mandatory {border-color:"""+neccol+""";}""")
        self.Window(parent)
    def Window(self,parent):
        fields=DF({"First Name":{'optional':False,'order':0},
                "Last Name":{'optional':False,'order':1},
                "Phone Number":{'optional':True},
                "Email":{'optional':True},"Business":{'optional':True}}) #some way to hide/show optional
        tfields=fields.T #easier for order inverting    
        fbox=QFormLayout()
        
        inps=dict()
        def makeline(i):
            fields[i]['box']=QLineEdit()
            inp=fields[i]['box']
            fbox.addWidget(inp)
            inp.setPlaceholderText(i) 
            if fields[i]['optional']==False:#if line is mandatory set stylesheet
                inp.setObjectName('mandatory')
#        for o in range(len(fields.T['optional'][fields.T['optional']==True])):
#            inp.setObjectName('optional')
        for o in range(len(fields.T[fields.T['order'].notna()].sort_values('order'))): #add the ones by order first
            rel=fields.T[fields.T['order']==o].index[0]
            makeline(rel)
        for i in fields.T[pandas.isna(fields.T['order'])].index: #now add ones for which order isn't important
            makeline(i)
        
        okbutt=QPushButton(text="OK",parent=self)
        cancbutt=QPushButton(text='Cancel')
        cancbutt.clicked.connect(self.close)
        fbox.addWidget(okbutt)
        fbox.addWidget(cancbutt)
        self.setLayout(fbox)
        
        def setcust(fields): #setts customer for this donation, need to make sure doesn't already exist in db, give option to select that already existing person and go thru w donation
            #if not in db already/make new version of cust
            name={str(i):dbFilter(fields[str(i)+' Name']['box'].text()) for i in FL} #inputs name as dict object
            p=parent#parent's self
            
            m=p.don.donor.lookupDonor(name) #checks if donor already in db
            
            if len(m)==0: #if not already in db, then 
                p.don.updateDonor(name)
                p.nmlbl.update(p.don.donor)
                self.close()
                logging.info('added donor f:'+name["First"]+ ' l:'+name['Last']+' to a donation')# include don id
            elif len(m)==1:
                failbox=QMessageBox()
                #failbox.buttonClicked[QAbstractButton].connect(lambda button:print(button))
                reply=failbox.question(self,"Duplicate Customer","Customer already exists! Set as current customer?")
                if reply==QMessageBox.Yes:
                    p.don.updateDonor(name)
                    p.nmlbl.update(p.don.donor)
                    self.close()
                elif reply==QMessageBox.No:
                        print('no')
        def check(fields):  #function checking if input is good goes here, only returns pass/fail
            numdone=0
            #nms is names of input boxes 
            
            nms=fields.T[fields.T['optional']==False].index #everything in fields for which optional is False
            notblank={x for x in fields.keys() if fields[x]['box'].text()!=''} #everything  
            if set(nms).intersection(notblank)==set(nms): #if the set of required names is in the set of not blank names:
                #print('passed check')
                return True #passes check
            else: 
                #print('didnt pass')
                return False #u guessed it 
            #set(nms).intersection(notblank)
        okbutt.clicked.connect(lambda: setcust(fields) if check(fields)==True else QMessageBox(text="Required Field(s) Missing!").exec()) #if fields pass check, then save the customer

class StatsWindow(QWidget): #window to look at statistics of donations
    """
    TO DO:
        reimplement timelen box w threads
        make b able toooo chooose which metrics r shown - multi box selection?
     
        Choose date
        'Show Categories' Checkbox
        
        
        statCategories:
            # of donors
            most popular days to donate
            normalized (focuses on which categories are most popular that day)
        
    """
#    def windowRun(self):
           
    def __init__(self,parent=None): #Header init
        
        super(StatsWindow,self).__init__()
        self.setMinimumSize(500,500)
        self.setLayout(QGridLayout())
        self.stack=QStackedWidget()
        self.layout().addWidget(self.stack)
        print()
        self.sel=self.selWindow(parent=self)
        self.stack.addWidget(self.sel)
        self.stack.setCurrentWidget(self.sel)
        self.stack.show()
        self.exp=self.exportWindow(parent=self)
        self.stack.addWidget(self.exp)
        self.setWindowTitle('Statistics')
        
#       
#        
#        self.windowThread=threader(self.windowRun)
#        self.windowThread.start()
    class selWindow(QWidget):
        def expfn(self):
                self.parent.stack.setCurrentWidget(self.parent.exp)  
        def __init__(self,parent=None): #Header init
          
            QWidget.__init__(self)
            
            def updategraphfn(rng=None):
                pass
#                if rng!=None:
#                    self.upto=datetime.datetime.now()-datetime.timedelta(rng)
#                else:
#                    self.upto=None
#                addstat('dategraph')
#                self.update()
#                self.layout().update()
#                self.statslayout.update()
#                #self.upto
            self.parent=parent
            self.ii=0
            self.setLayout(QGridLayout())
            self.bar=QProgressBar()
            self.bar.hide()
#                self.layout().addWidget(self.bar,10,0)
#            print('test1')
            timeslice=QComboBox()
            slices={'':None,'Yearly':365,'Monthly':30,'Weekly':7,'Daily':1,}
            timeslice.addItems(slices.keys())
            timeslice.currentIndexChanged[str].connect(lambda i:updategraphfn(slices[i]))
#            print('test2')
            self.layout().addWidget(timeslice,0,0)
           
            expbtn=QPushButton('Export Statistics (in progress)')#make able to auto send thru email auto
            expbtn.clicked.connect(self.expfn)
            self.layout().addWidget(expbtn,99,0,alignment=QtCore.Qt.AlignBottom)
#            print('test3')
           
            self.upto=None
            self.statslayout=QGridLayout()#layout on which widgets w statistics will be laid out
            self.layout().addLayout(self.statslayout,1,0)
#            print('test4')
            self.stats={'ndons':{'typ':'str','str':'Number of Donations','fn':lambda: len(self.data['dons'])},
                       'ndonors':{'typ':'str','str':'Number of Donors','fn':lambda: len(self.data['donors'])},
                       'maxdon':{'typ':'str','str':'Donor with most donations','fn':lambda:self.statfns.maxdonfn()},
                       'popdate':{'typ':'str','str':'Most popular date to donate','fn':lambda:self.statfns.popdatefn()},
                       'dategraph':{'typ':'graph','str':'Popular Donation Days','fn':lambda:self.statfns.dategrafn(bar=self.bar)}}
            
            
            self.statfns=Stats()
            self.statfns.retrieveData()
            self.data=self.statfns.data
            print('retrieved data')
            self.statthreads=dict()
            self.statobjs=dict()
#            print('test5')
#            class threader1
            self.addStats()
#            print('test6')
       
            
        def addStats(self):
            def addthreadres(items,ii=None):
                for i in items:
                    if type(i)==str:
    ##                    print(str(i)+str(i.thread()))
    #                    i.moveToThread(self.thread())
                        self.statslayout.addWidget(QLabel(i))
                    else:
                        canvas=FigureCanvas(i)
                        toolbar = NavigationToolbar(canvas,parent=None)
                        self.statslayout.addWidget(canvas)
                        self.statslayout.addWidget(toolbar)
                
#                    self.statslayout.update()
              
            for i in self.stats.keys():#makes an individual thread for each stat rendered
#                self.statthreads[i]=QtCore.QThread()
           
                self.statobjs[i]=StatThread(stats=self.stats,i=i,ii=self.ii,upto=self.upto)
#                self.statobjs[i].moveToThread(self.statthreads[i])
#                self.statthreads[i].started.connect(self.statobjs[i].calcStat)
                self.statobjs[i].start()
                print('started '+i)
                self.statobjs[i].calculated.connect(addthreadres)
                self.statobjs[i].failed.connect(lambda:print('failed'))
               # self.statslayout.addWidget(QWidget(),self.ii,0)
                
                self.ii=self.ii+1
#            self.statthreads['dategraph'].finished.connect(self.bar.hide)
   
    class exportWindow(QWidget):
        """TO DO
            make selected upto work
            Implement custom time ranges
        """
        
        def __init__(self,parent=None): #Header init
            QWidget.__init__(self,parent)
            self.upto=datetime.datetime.now()-datetime.timedelta(7)
            self.parent=parent
            lay=QGridLayout()
            self.setLayout(lay)
            def backfn():
                self.parent.stack.setCurrentWidget(self.parent.sel)
           
            backbtn=QPushButton("Go Back")
            self.layout().addWidget(backbtn,0,0,alignment=QtCore.Qt.AlignTop)
            backbtn.clicked.connect(backfn)
            
            lens={"Last Week":dict({'time':7}),"Last Month":dict({'time':30}),"Last Year":dict({'time':30}),"Custom":dict({'time':None})}#
            
#            self.layout().addWidget(QLabel('Export Donation Statistics Since The Last...',font=QtGui.QFont('helvetica',15)))
         #   self.butts=QButtonGroup()
          #  self.layout().addWidget(butts)
            
#            for i in lens.keys():
##                lens[i]['rad']=QRadioButton(i,self)
#              
#               # self.butts.addButton(lens[i]['rad'])
#                #self.butts.setId(lens[i]['rad'],i)
#                lens[i]['rad'].clicked.connect(lambda :print('test'))
#              #  self.layout().addWidget(lens[i]['rad'])
            def savexlfn(mail=False):
                
                dialog=QFileDialog.getSaveFileUrl(filter="Excel (*.xls)")
                self.saveloc=dialog[0].path()[1:].replace("\\", "\\\\")
                print(self.saveloc)
                self.bar.show()
                class calcthread(QtCore.QThread):
                    def __init__(self,statfns,dialog,upto=None,bar=None):
                        super(calcthread,self).__init__()
                        
                        self.stats=statfns
                        self.saveloc=dialog[0].path()[1:].replace("\\", "\\\\")
                        print(self.saveloc)
                        
                        self.upto=upto
                        self.bar=bar
                        
                    def run(self):
                        self.stats.savexl(saveloc=self.saveloc,fn=self.stats.popdatefn(ret='full',cat=True,bar=self.bar,upto=self.upto))
                self.thread=calcthread(self.parent.sel.statfns,dialog,upto=self.upto,bar=self.bar)
#                self.bar.hide()
                self.thread.start()
                logging.info('started write to excel')
                self.thread.finished.connect(self.bar.hide)
                def mailfn():
                  try:
                      OHMailer.send(self.emailinp.text().strip(),filenm=self.saveloc)
                      print('sent')
                      self.emailinp.clear()
                  except:
                      print('failed :(')
                      raise
                if mail:
                    self.thread.finished.connect(mailfn)
                
                 
            #    print(DF(file),'test')
            #make an option (checkbox?) for emailing - calls a fn which calculates the popdatefn every once in a while (every 7 days on startup)
            filelocbtn=QPushButton("Choose where to save")
            filelocbtn.clicked.connect(lambda:savexlfn())
            self.layout().addWidget(filelocbtn,1,0)
            self.bar=QProgressBar()
            self.bar.hide()
            self.layout().addWidget(self.bar,100,0)
            
            #email stuff - needs to be able to check if double-sending
            def addmailschedfn():
                addy=self.emailinp.text().strip()
                def testadd(addy):#tests if add is valid
                    
                    if '@' and '.' in addy:
                        return True
                    else:
                        return False
                    
                    
                res=testadd(addy)
                if res:
                    pass
                    
                else:
                    QMessageBox(text='Invalid Email Entry!').exec()
           
            box=QGroupBox('email last seven days')
            schedbox=QGroupBox('Get Donations emailed weekly (in progress!)')
            schedbox.setCheckable(True)
            box.setFlat(True)
            schedbox.setEnabled(False)
            box.setMaximumHeight(100)
            box.setLayout(QHBoxLayout())
            self.emailinp=QLineEdit()
            addreminderbtn=QPushButton("Save then send to Email")
            addreminderbtn.clicked.connect(lambda: savexlfn(mail=True))
            box.layout().addWidget(self.emailinp)
            
            box.layout().addWidget(addreminderbtn)
            self.layout().addWidget(box)
            self.layout().addWidget(schedbox)
def addtosched(addy,time):
    name=addy.split("@")[0]+addy.split("@")[1].split('.')[0]#task name
    ts = pythoncom.CoCreateInstance(taskscheduler.CLSID_CTaskScheduler,None,

                                    pythoncom.CLSCTX_INPROC_SERVER,

                                    taskscheduler.IID_ITaskScheduler)
    if '%s.job' % name not in ts.Enum():

        task = ts.NewWorkItem(name)
        
        #define task fn here
        
        
        task.SetPriority(taskscheduler.REALTIME_PRIORITY_CLASS)

        task.SetFlags(taskscheduler.TASK_FLAG_RUN_ONLY_IF_LOGGED_ON)

        task.SetAccountInformation('', None)

        ts.AddWorkItem(name, task)

        tr_ind, tr = task.CreateTrigger()

        tt = tr.GetTrigger()

        tt.Flags = 0

        tt.BeginYear(datetime.datetime.strftime('%Y',time))
        
        tt.BeginDay
        
        tt.BeginMonth
        
        #startmin/hour here too
        
        tt.TriggerType = int(taskscheduler.TASK_TIME_TRIGGER_WEEKLY)

        tr.SetTrigger(tt)

        pf = task.QueryInterface(pythoncom.IID_IPersistFile)

        pf.Save(None,1)

        task.Run()
    task = ts.Activate(name)

    exit_code, startup_error_code = task.GetExitCode()

    return win32api.FormatMessage(startup_error_code)

def dockrun():
    app=0         
    #windthread=QtCore.QThread()
    
    def thrdrun():
        app=QApplication(sys.argv)
        wind=DonationWindow()
        app.exec_()
    try:
        thrdrun()
        return True
    except:
        raise
#    windthread.run=thrdrun()
#    windthread.finished.connect(windthread.quit)
#    windthread.start()
"""
GENERIC CLASSES - non GUI-framework-specific stuff goes below here


Need 2 Do List:
    Receipts!!!
    test write to db
    Editable Receipts too
    Get old receipts if wanted
    IDs generation
    """    
    
class Donation(object): #make each donation a discrete object, with its own time, associated customer, and values
    def __init__(self,donor=None,ID=None,date=None):
        
        self.items=dict()
        
        if date==None:
            self.date=datetime.datetime.today()
        else:
            if type(date)==str:
                try:
                    self.date=datetime.datetime.strptime(date,'%d.%m.%Y')
                except:
                    self.date=datetime.datetime.strptime(date,'%Y-%m-%d %H:%M:%S.%f')
            elif type(date)==datetime.datetime:
                self.date=date
        self.timestamp=self.date
        
        if donor!=None:
            self.updateDonor(donor)
        else:
            self.donor=Donor()
        if ID is None: #if not given id, make one
            self.ID=self.generateID()
            print(self.ID)
        else:
            self.ID=ID
    def updateQuant(self,item,quant): #needs to be own fn for button to connect to 
        if quant!=0:
            self.items[item]=quant
        else:#is zero, remove from list
            if item in self.items.keys():
                self.items.pop(item) #updating to 0 should be same as popping
            
    def updateDonor(self,donor):
        self.donor=Donor(name=donor) 
        
    def saveDonation(self): 
        
      

      #  try: #do more substantial stuff here to check things similar to check fn in address book? ie all necessary parts filled out
      succ=donstodb([self],path=dbpath,write=1) 
      if succ==Exception: 
            logging.error("Add into DB failed f:"+self.donor.name["First"]+" l:"+self.donor.name["Last"]+" donated:" +','.join([str(self.items[it])+'x '+str(it) for it in self.items.keys()])+" on: "+str(self.timestamp))
            return False#didn't succeed
      else: 
         # print(succ)    
          return True
    def generateID(self):
        #generate by adding to last one?
        lastid=connwrite(dbpath,('SELECT MAX(id) FROM Donations',))[0][0]#needs last comma in order to be a tuple
        tempstamp='55555' #
        s=str(int(lastid))
        if s.find(tempstamp)!=-1:
            tempid=tempstamp+str(int(s[s.find(tempstamp)+len(tempstamp):])+1)
        else:
            tempid=int(lastid)+1
        return tempid
    def text(self):
        don=''
        for i in self.items.keys():
            don=don+str(self.items[i])+' '+str(i)
            if self.items[i]>1:
                don=don+"\'s"
            don=don+', '
            
        string=self.donor[1]+' '+self.donor[0]+' donated:'+don+' on '+self.timestamp
        return str()
    
class Donor(object): #Donor object, connects personal info to donation ID's
    def __init__(self,name=None,**kw): #for this input, assume name is 
        self.donations=[] #IDs - do smth to get these? method?
        self.name=dict(zip(FL,[None,None]))  #easy shorthand for dict whos values are None 
        if type(name)==str: #splices string to dict
            spl=str(name).split(',')
            if len(spl)>2:
                spl=[spl[0].strip(),'!'.join(spl[1:])] #to handle longer than 2 commas, mark to get around to later during db cleanup
            if len(spl)<2:
                spl=str(name).split(' ')
                if len(spl)<2:
                    spl=[str(name),'']
            for i in range(len(FL)):
                try:
                    self.name[FL[i]]=spl[i].strip()
                except TypeError: self.name[FL[i]]=None
            
        elif type(name)==dict: #if splicing not necessary for this input
            if set(name.keys())==set(FL): #if dict already in right format 
                self.name=name
            else: #not in right dict format
                self.name["First"]=name
        if set(self.name.values())!={None}: #if there's a donor associated w this donation then add an ID
            self.IDfn()
    @property#automagically updates
    def stringName(self):#can do in * method 
        return dbFilter(str(self.name['First'])+' '+str(self.name['Last']))
    def addDonations(donations): #start with blank donation? 
        #do something to make sure it's a donation
        self.donations=[*self.donations,*[i.ID for i in donations]]  #add each ID  (append wouldn't work to add multiple at a time)
    def loadDonations(self): #loads old donations for this donor
        pass
    def IDfn(self):#if ID is in db already, 
        match=self.isindb(retmatch=True)
        if match[0]==True:
           pass #print(match[1])
        else: #not already in db, 
            self.generateID()
            
    def generateID(self):
        pass

    def lookupDonor(self,name=None): #looks up if donor obj exists in db
        if name==None:
            name=self.name
        #print(name)
        match=connwrite(dbpath,("""SELECT * FROM donors 
                                 WHERE (Firstname=? AND Lastname=?) OR (Firstname=? AND Lastname=?) """,(dbFilter(name['First']),dbFilter(name['Last']),dbFilter(name['Last']),dbFilter(name['First']))))
        logging.debug('looked up '+str(name['First'])+','+str(name['Last'])+' in db, '+str(len(match))+' matches') #checking that everything's going ok here
        return match
    def isindb(self,retmatch=False):#retmatch - include match in return if True
        r=self.lookupDonor()
        
        if len(r)!=0:
            if retmatch==True:
                return [True,r]
            else:
                return True
        else:
            if retmatch==True:
                return [False,r]
            else:
                return False
    #these functions only interfaced to from AddCustWindow
    def addDonor(self):#Handler function to add new donor into database
        match=lookupDonor()
        if len(match)==2: 
            self.resolveConflict() #resolve  somehow
        elif len(match)==1: 
            self.updateDonor()#Already exists update user if that would be of use
        elif len(match)==0: 
            self.saveDonor()#write to db as new user
    def resolveConflict(self): #if donor exists in duplicate in the db, or appears to? dunno what to do rly other than check against phone # or smth
        print("whoops lol")
    def updateDonor(self): #if I wanna do something with receipt codes or something?
        pass#self.saveDonor()
    def saveDonor(self):#Saves new donor
        try:
            connwrite(dbpath,"INSERT INTO Donors VALUES Firstname=?,Lastname=?",(dbFilter(self.name['First']),dbFilter(self.name['Last'])))#
            logging.info("Saved f:"+self.name["First"]+' l:'+self.name["Last"]+' into db')
            return True
        except:
            return False

class Receipt(object): #only sees list of don objects, interfaced with either when a donation is saved or when ppl want a receipt of old donations
    
    def __init__(self,dons):#dons must be a list all from same person -  
        super(Receipt,self).__init__()
        url='http://opportunityhouse.us/'
        twi='https://twitter.com/VacavilleOHouse'
        inst='https://www.instagram.com/opportunitythrift/'
        ratio=[1,2]#doesn't rly make sense w changing len
        self.defres=300#don't change this, used to scale items on pg
        self.res=1000
        self.name=dons[0].donor.stringName #name should b the same for all don's
        self.n=len(dons)
        self.dons=dons
        self.imsize=tuple([self.res*i for i in ratio])
        
    @property 
    def resrat(self):
        return self.res/self.defres
    def centerfn(self,c,imsize=None):
        if imsize==None:
            imsize=self.imsize
        return [round(imsize[i]*c[i]) for i in range(len(c))]   
    def render(self):#break up receipt into 3 sections?
        #SECTIONS:
            #Logo
            #Donations
            #---Don1 (total 0)
            #---....
            #Tax Blurb
            #Social Media stuff
            
            
        #printer width - 80mm - 203x203 dots per inch
        
        ndons=len(self.dons)#number of discrete donations
        ndonlines=[len(i.items) for i in self.dons ] #list w numbers of lines per donation
        taxid='68-0364021'
        taxblurb="No goods or services were \n received in return for this contribution. Thank You!"
#        d=int([])#TEMP
        d=0
        totalblurb="Total: $"+str(d)+".00"
        
        #LOGO
        logo=Image.open(open(wd+r'\Visuals\Logo\bwlogo.png','rb'))
        logores=round(750)
        logorat=logo.size[1]/logo.size[0] #make x coord=1
        logo=logo.resize((logores,round(logores*logorat)))#maintains aspect ratio
        logosect=Image.new('RGB',self.imsize,color="white")
        
        self.img=Image.new('RGB',self.imsize,color="white")
        #topsect=ImageDraw.Draw()
        cropbox=[(self.img.size[0]-logo.size[0])/2,0,(self.img.size[0]+logo.size[0])/2,logo.size[1]]
        
        logosect.paste(logo,[round(x) for x in cropbox])
        logosect=logosect.crop([0,0,self.imsize[0],logo.size[1]])
        logosz=logosect.size[1]
        #img=Image.new('RGB')
        #receipt header: ~20, each donation: 5, each line: 2, bottom: ~10? sm ratio like that 
#        multdict=dict([[] for i in self.items.keys()])}
#        multidict['Dump Fee']='$'
        
        dontxtstr=[' \n '.join([*['$: '.join([str(i.items[j]),str(j)]) if j=='Dump Fee' else 'x: '.join([str(i.items[j]),str(j)]) for j in i.items.keys()],totalblurb]) for i in self.dons]
        #i=self.dons[0]
        
        #dontxtstr=' \n '.join(['x: '.join([str(i.items[j]),str(j)]) for j in i.items.keys()])
        #print(dontxtstr)
        d=ImageDraw.Draw(self.img)
        f=ImageFont.truetype('timesbd.ttf',round(13*self.resrat))
        dlf=ImageFont.truetype('timesbd.ttf',round(13*self.resrat))
          
        dist=30 #distance between donation header and first don
        dldist=30#distance between each donline
        lasty=0#y pos last part went to, useful in placing 
        rhsbuffer=10 #how far adjusted text is from right hand side
        
        donsect=Image.new('RGB',self.imsize,color="white")
        dond=ImageDraw.Draw(donsect)
        for i in range(len(self.dons)):#EACH i IS A DONATION, with its own items
            
            date=self.dons[i].date.date()
            
            if i==0: 
                 donstr="On %s, %s donated:"%(str(date),self.name) #don
                 print(donstr)
                 #place don
            else:
                donstr="And on %s, %s also donated:"%(str(date),self.name)
                #place these dons
           
            #sizes
            dtsize=ImageDraw.ImageDraw.multiline_textsize(dond,text=donstr, font=f)
            dlattsize=ImageDraw.ImageDraw.multiline_textsize(d,text=dontxtstr[i], font=dlf,spacing=dldist)
            
            tempy=lasty+dtsize[1]+dlattsize[1]+dist #temporary lasty, here used to make sure text won't be off the page - temporary?
            if tempy>=donsect.size[1]:
                pass#change size
            else:
                #placing text
                dond.text([self.imsize[0]-(dtsize[0]+rhsbuffer),lasty],text=donstr,font=f,fill='black')
                dond.multiline_text([self.imsize[0]-(dlattsize[0]+rhsbuffer),round(dtsize[1]+lasty)],text=dontxtstr[i],font=dlf,spacing=dldist,fill='black')
            #d.multiline_text([self.imsize[0]-dlattsize[0]-round(self.resrat*10),logo.size[1]+round(((n)*dist)*self.resrat)],text=dontxtstr[i],font=f,spacing=dist,fill='black')
                lasty=tempy
           # recsect.paste(donsect.crop())
            #self.tag.paste(attag.crop(attbox),box,mask=ImageOps.invert(attag.crop(attbox)))
        donsect=donsect.crop([0,0,self.imsize[0],lasty])
        donsz=donsect.size[1]
        
        
        
        #tax
        taxsect=Image.new('RGB',self.imsize,color="white")
        taxd=ImageDraw.Draw(taxsect)
        taxf=ImageFont.truetype('timesbd.ttf',round(11*self.resrat))
        taxstr='501(c)(3) tax#: '+taxid+ ' - ' +taxblurb
        taxsz=taxd.multiline_textsize(text=taxstr,font=taxf)[1]
        taxd.multiline_text(self.centerfn([.075,0]),text=taxstr,font=taxf,fill='black') #need to center this
        taxsect=taxsect.crop([0,0,self.imsize[0],taxsz])
        
        #soc
        socheight=.3
        
        socsect=Image.new('RGB',[self.imsize[0],round(socheight*self.res)],color="white")
        socd=ImageDraw.Draw(socsect)
        socf=ImageFont.truetype('timesbd.ttf',round(10*self.resrat))
        soc={'insta':{'page':'@OpportunityThrift','c':[.1,.15],'tc':[-.9,.2]},
                      'twitter':{'page':'@VacavilleOHouse','c':[.1,.95],'tc':[-.9,.9]},
                      'fb':{'page':'OpportunityHouseVV','c':[.9,.15],'tc':[3.4,-.5]},
                      'web':{'page':'www.OpportunityHouse.US','c':[.9,.95],'tc':[3.4,.25]}}#key acts as filename, value is center%
        for j in soc.keys():
            c=self.centerfn(soc[j]['c'],imsize=socsect.size)#returns percentage into pixels
            
            setattr(self,j,Image.open(open(wd+r'\Visuals\%s.png'%j,'rb')))
            q=getattr(self,j)
            q=q.resize((round(q.size[i]*self.img.size[0]/(q.size[0]*10)) for i in [0,1])) #makes all same size in x
            
            tsize=ImageDraw.ImageDraw.multiline_textsize(socd,text=soc[j]['page'])[0]
            b=[round(c[i]-q.size[i]*soc[j]['c'][i]) for i in range(len(c))]#box
            tb=[round(c[i]-tsize*soc[j]['tc'][i]) for i in range(len(c))]#textbox
        
            socsect.paste(q,b,q)#do smth abt size
            #textgap=[0.15,.025]
            textgap=[0,0]
            if soc[j]['c'][0]<.5:  #LHS SCALING
                sign=-0
            else:#RHS SCALING
                sign=-2.5
            socd.text(tb,text=soc[j]['page'],font=socf,fill='black')
        socsz=socsect.size[1]
#        socsz=0
#        
       #PASTE EVERYTHING HERE FOR EASE OF READING
        size=0
        
        rcptim=Image.new('RGB',[self.imsize[0],logosz+donsz+taxsz+socsz],color='white')
        for i in [logosect,donsect,taxsect,socsect]:
            nsize=size+i.size[1] 
            print(nsize,rcptim.size)
            rcptim.paste(i,(0,size))
            size=nsize
       #logosect
        #donsect
        #taxsect
        #socsect
        return rcptim
            #
class StatThread(QtCore.QThread):
    percdone=QtCore.pyqtSignal(float)
    calculated=QtCore.pyqtSignal(list)
    failed=QtCore.pyqtSignal()
    def __init__(self,i,stats,ii,upto=None):
        super(StatThread,self).__init__()
        self.i=i
        self.stats=stats
        self.ii=ii
        self.ax=None
        self.upto=upto 
    @QtCore.pyqtSlot()#wraps this fn into a slot from where its accessible outside of a thread
    def run(self):
        i=self.i
#        print(i)
        if self.stats[i]['typ']=='str':
            try:
                calcstr="<b>"+self.stats[i]['str']+": </b>"+str(self.stats[i]['fn']())
                self.calculated.emit([calcstr])
                print('calced '+i)
                
                
            except:
                print('failed '+i)
                self.failed.emit()
#                            raise#if u need to debug why the stat's not calcing
        elif self.stats[i]['typ']=='graph':
            
            try:
                data=self.stats[i]['fn']()
               
                if self.ax==None:
                    
                    self.fig=mp.figure()
                    
                    self.ax=mp.gca()
                    
                    self.ax.clear()
                    
                    self.ii=self.ii+2
                else:
                    
                    self.ax.clear()
                ps=dict()
                if list(data.keys())!=[]:
                    if type(data[list(data.keys())[0]])==dict:#if dict is embedded - 
                        dd=DF(data)
                        
#                                self.ax.hold(True)
                        bottom=np.zeros(len(dd.T))
                        l=len(dd.T.keys())
                        jj=0
                        for j in dd.T.keys(): 
                            ps[j]=self.ax.bar(dd.keys(),dd.T[j],bottom=bottom)
                            bottom=bottom+np.array(dd.T[j])
#                                self.ax.hold(False)
#                            self.percdone.emit(jj/l)
                            jj=jj+1
                    else:
                        ps['dons']=self.ax.bar([str(i) for i in data.keys()],data.values(),color='green')
                self.ax.legend(ps.keys())
                if self.upto is not None:
                    datestr=self.upto.strftime('%D')+' - '+datetime.datetime.now().strftime('%D')
                   
                else:
                    datestr=''
                self.fig.suptitle(self.stats[i]['str']+' '+datestr)
                
              #  
                self.calculated.emit([self.fig])
                print('calced '+i)
            except:
                print('failed '+i)
                self.failed.emit()
                raise  
class Stats(object):#make stats into own class so it can keep track of things already calculated/accessible from outside
    
    def __init__(self,data=None,upto=None):
        if data is None:
            self.data=self.retrieveData()
        elif data is not None:
            self.data=data
#        else:
        self.calcd=dict()#already calculated values w params
        self.upto=upto
    def dayshiftfn(self,days,n=0,lr='l'):
#        print(days)
        days={i:(days[i]+n)%7 for i in days}
        return days
    def retrieveData(self):
        
        data=dict()
        data['lines']=connwrite(dbpath,("SELECT * FROM Donationlines",))
#            print('lines')
        data['donors']=connwrite(dbpath,("SELECT * FROM Donors",))
#            print('donors')
        data['dons']=connwrite(dbpath,("SELECT * FROM Donations",))
#            print('dons')
        data['cats']=connwrite(dbpath,("SELECT * FROM CategoryMap JOIN DonationCategories ON mapstoid=DonationCategories.id",))#Join this w donationcats
#            print('cats')
        return data
    def savexl(self,saveloc,fn):
        days={'Monday':0, 'Tuesday':1, 'Wednesday':2,'Thursday':3,'Friday':4,'Saturday':5,'Sunday':6}
               
        if saveloc!='':
            
            try:
                data=DF(fn)
#                print(data)
                
                writer=pandas.ExcelWriter(saveloc)#[1:])
                
#                print('test????')
                sortdates=sorted(days,key=lambda day:self.dayshiftfn(days,-days[datetime.datetime.today().strftime('%A')])[day])
               
                print('test?')
                data[sortdates].to_excel(writer,startcol=1,startrow=1)
                
                print('test')
                if self.upto!=None:
                    timestr=self.upto.strftime('%D')+' - '+datetime.datetime.now().strftime('%D')
                else:
                    timestr=''
                print(timestr)
                writer.sheets['Sheet1'].write(0,0,timestr)
                writer.save()
                print('write xl done!')
                return True
            except:
                raise
                return False
        
    def maxdonfn(self):
        maxdon=DF(self.data['dons'])[1].value_counts()
       
        maxdonid=int(maxdon.index[1])
        return str(self.data['donors'][maxdonid][1])+' '+str(self.data['donors'][maxdonid][2])
    def dateparsefn(self,inp,attr='%A',upto=None):#building block of date fns
        str0='%d.%m.%Y'
        str1='%Y-%m-%d %H:%M:%S.%f'
        try:
            ret=datetime.datetime.strptime(inp,str0)
           
        except ValueError:
            
            try:
               
                ret=datetime.datetime.strptime(inp,str1)
               
            except:
                print('eh')
                raise
        if upto is not None:
          
            if ret<upto:#if the return date is farther back than upto, return false
               
                return False
            
        return ret.strftime(attr)
        
    def popdatefn(self,ret='max',cat=False,strp='%A',upto=None,bar=None): #Calculates #dons/day - make able to save into cache
        print(len(self.data['dons']))
        if cat==False:
            ndays={'Monday':0,'Tuesday':0,'Wednesday':0,'Thursday':0,'Friday':0,'Saturday':0,'Sunday':0}#number of days - if needs cats will have subdicts
        
            for i in self.data['dons']:
                
                day=self.dateparsefn(i[2],strp,upto=upto)
                
                if day==False:
                   
                    continue
                elif day in ndays.keys():
                    ndays[day]=ndays[day]+1
                else:
                    ndays[day]=1
        else: #Include Cats
            #REALLY SKETCHY
            ndays={'Monday':dict(),'Tuesday':dict(),'Wednesday':dict(),'Thursday':dict(),'Friday':dict(),'Saturday':dict(),'Sunday':dict()}#number of days - if needs cats will have subdicts
        
            p=DF(self.data['lines'])#pandas easier to work w
            if bar!=None:
                bar.setMaximum(len(p[0]))
            d=DF(self.data['dons'])
            c=self.data['cats']
            ii=0#donation number index
            jj=0#donation order index
            date=''

            for j in range(len(p[1])): #for each donation line
                if bar!=None:
                    bar.setValue(j)
                it=c[p[2][j]][-1]
                
                if p[1][j]!=ii:#donation index has changed
                    ii=p[1][j]
                    jj=d[0][d[0]==ii].index[0]
                    day=self.dateparsefn(d[2][jj],upto=upto)
                  
                    jj=jj+1
                if day==False:
                    continue
                
                if it in ndays[day].keys():#if this item is already a
                    ndays[day][it]= ndays[day][it]+p[3][j]
                else:
                    ndays[day][it]= p[3][j]
        days=['Monday', 'Tuesday', 'Wednesday','Thursday','Friday','Saturday','Sunday']
        ndays={i:ndays[i] if i in ndays.keys() else {i:0} for i in days}
        if ret=='max':
            return max(ndays,key=ndays.get)
        elif ret=='full':
            return ndays
    def dategrafn(self,bar=None,upto=None):#need to be able to indicate categories
        return self.popdatefn(ret='full',cat=True,upto=upto,bar=bar)
    
        

#need to include q info in some sorta serialized cache - checks/processes on startup
#keeps track of last sent date 
class QMail(object):#Queue item
    def __init__(self):
        pass
    def addToQ(self):
        pass
    def remFromQ(self):
        pass
    def processQ(self,item):
        pass
    
        

"""METHODS TO WORK WITH DATABASES BELOW HERE 
 
 Need 2 do list:
     check if donation already exists in db !!!!
     add more error catching
     make donorids go faster for big data
     revisit Splice & clean up 
     rollbacks/closing
     look into other sorts of dbs?
     more filtering
 """
 
def QuickSplice(path=None):
    #r'C:\Users\V\Python\Data\customer db1/2/3.csv'
    data=pandas.read_csv(path,header=5)
    newdata=DF()
    
    #each date is a unique donation, input the donations and other details
    events=data[data['Date'].notna()]
    #data['Type'].str.contains("receiving",flags=re.IGNORECASE) ignore case - no longer useful but syntax may be in future
    donations=[]
    for i in events.index: #each i is a donation
        n=events['No. of Items'][i] #number of different items in this donation
        
        donations.append(Donation(donor=events['Vendor'][i],ID=events['Voucher #'][i]))
        d=donations[-1] 
        d.timestamp=events['Date'][i] 
        
        for x in range(i+1,i+int(n)+1):
            
            try:
                if pandas.isna(data['Date'][x]):
                    don=False
                
                if pandas.isna(data['Type'][x]):#in the few hundred blips where type is blank, looks to be some sort of bug or mis-inputted data
                    break #breaks out of step in forloop if type is blank 
                if data['Type'][x].lower()!='receiving': #if Type column isn't 'receiving', quickbooks/old system puts the category name here
                    d.updateQuant(data['Type'][x],data['Total Qty'][x])
                elif str(data['Vendor'][x]).find('x000D_\n')!=-1:
                    d.updateQuant(data['Vendor'][x].split('x000D_\n')[1],data['Total Qty'][x])
                else:      
                    d.updateQuant(data['Voucher #'][x],data['Total Qty'][x]) #newest vals
            except KeyError:
               if x>=len(data):
                    don=False                   
    return donations 
def donstodb(dons,path='test.db',write=0,inps=['All']): #writes list of Donation objects to database
    #timer=Timer()
    
    conn=sqlite3.connect(path)
    c=conn.cursor()
    #if wanna do foreign keys: https://sqlite.org/foreignkeys.html#fk_enable
    #Tables - make donorids not null after done setting up db
    c.execute('CREATE TABLE IF NOT EXISTS Donations(id INTEGER NOT NULL PRIMARY KEY,donorid INTEGER, timestamp TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS DonationCategories(id INTEGER NOT NULL PRIMARY KEY,name TEXT)')
    c.execute("CREATE TABLE IF NOT EXISTS CategoryMap(id INTEGER, name TEXT, mapstoid INTEGER )")
    c.execute('CREATE TABLE IF NOT EXISTS Donors(id INTEGER PRIMARY KEY, Firstname Text,Lastname TEXT)') #donations is text list of donations separated only by comma
    c.execute("""CREATE TABLE IF NOT EXISTS DonationLines(id INTEGER NOT NULL PRIMARY KEY, 
                                                          donationid INTEGER NOT NULL REFERENCES Donations(id),
                                                          categoryid INTEGER NOT NULL REFERENCES CategoryMap(id),
                                                          quantity INTEGER NOT NULL);""") #new donationline is added for each category donated
    
    #make these into pandas? will prob make life easier
    
    inpmap={'line':'DonationLines','cat':'CategoryMap','don':'Donations','donor':'Donors'}
    catmap=buildCatmap() #do smth if not buildable for some reason?
    
    if inps==['All']:
        inps=inpmap.keys()
        
    #Pick out relevant info in dons fed in here
    times=[datetime.datetime.strptime(i.timestamp,'%d.%m.%Y') if type(i)==str else i.timestamp for i in dons]
    items=[i.items for i in dons]
    donors=[i.donor.name for i in dons] #list of each donor dict for each don - will derive both associated donor ID and donor set from this
    donids=[int(i.ID) for i in dons] #ids for each donation
    
    #dataframe containing alla that
    df=DF({'donors':donors,'ids':donids,'items':items})
    
    #uniques
    tits=[set(i.keys()) for i in items] #all the item names
    cats=list(set().union(*tits)) #turns into all unique item names 
    cats=[dbFilter(i,str) for i in cats]
    
    donornames=DF(donors).drop_duplicates()#list of unique donors
    donornames.index=range(len(donornames)) #reset index to go from 0 without gaps
    
    brkchr='!!'#character that splits names in dbdonors
    #Check which categories/donations/donors already 
    dbcats=set(c.execute("SELECT * FROM CategoryMap WHERE name IN ("+','.join(("?" for q in cats))+")",[dbFilter(i) for i in cats]).fetchall())
    dbdons=set(c.execute("SELECT * FROM Donations WHERE id IN ("+','.join(("?" for q in donids))+")",[dbFilter(i) for i in donids]).fetchall())
    dbdonors=set(c.execute("SELECT * FROM Donors WHERE Firstname||'"+brkchr+"'||Lastname IN ("+','.join(("?" for q in donornames.T))+")",[i for i in [brkchr.join(donornames.T[n]) for n in range(len(donornames))]]).fetchall())
 
    #get highest IDs here for purposes of inputting new donation IDs
    dbids=dict() #dict of max ids for each relevant input
    for j in inps:
        dbids[j]=c.execute("SELECT MAX(id) FROM "+inpmap[j]).fetchall()[0][0] 
        if dbids[j] is None:
            dbids[j]=-1
    #these defined bc used later 
    
    #get rid of entries already in db here - 
    winps=dict()#inps to write to - change name maybe
    if 'cat' in inps:
        winps['cat']=list(set(cats).difference(set([i[1] for i in dbcats])))
    if 'donor' in inps:
        winps['donor']=list(set((tuple(i.tolist()) for i in donornames.values)).difference(set([(i[1],i[2])for i in dbdonors])))
    
   #handle donors and lines here:
    donoridmap=dict([((i[1],i[2]),i[0]) for i in dbdonors]) #gives a dictionary w inps as names and outp as id
    for m in range(len(winps['donor'])):#adds donors not already in db into map w/ numbering
        donoridmap[winps['donor'][m]]=dbids['donor']+m+1
    
    quants=[int(it) for sublist in items for it in sublist.values()]#flattens out items into list of values
    linecatids=[catmap[it.lower()] for sublist in items for it in sublist.keys()]
    lids=[len(items[i])*[donids[i]] for i in range(len(dons))]#temp list of lists
    linedonids=[i for l in lids for i in l]
#    
    
    objs=dict()
    #ORDER WITHIN EACH ZIP VERY IMPORTANT
    objs['donor']=zip(range(dbids['donor']+1,dbids['donor']+len(winps['donor'])+1),#DonorID,
                 [i[1] for i in winps['donor']],   #First Name
                 [i[0] for i in winps['donor']])   #Last Name
    objs['don']=zip(donids,      #Donation ID,
               times,       #Donation Timestamp,
               (donoridmap[(i.donor.name['First'],i.donor.name['Last'])] for i in dons))    #DonorID
                
    objs['cat']=zip(range(dbids['cat']+1,dbids['cat']+len(winps['cat'])+1),#CategoryMapID
               winps['cat'],                           #Category Name
               [catmap[w] for w in winps['cat']])      #Category Maps to
             
    objs['line']=zip(range(dbids['line']+1,dbids['line']+1+len(quants)),#LineID
                   linedonids,                      #DonationID
                   linecatids,                      #CategoryMapID
                   quants)                          #Quantity
   
    def writefn(inps):
        c.execute("BEGIN TRANSACTION")
       
        try:
            
            print('began')
           # for i in inps: #need to be able to determine name of columns
            if 'cat' in inps:
                c.executemany("INSERT INTO CategoryMap(id,name,mapstoid) VALUES (?,?,?)",list(objs['cat']))
                print('cat')
            if 'don' in inps:
                c.executemany("INSERT INTO Donations(id,timestamp,donorid) VALUES (?,?,?)",list(objs['don']))
                print('don')
            if 'donor' in inps:
                c.executemany("INSERT INTO Donors(id,firstname,lastname) VALUES (?,?,?)",list(objs['donor']))
                print('donor')
            if 'line' in inps:
                c.executemany("INSERT INTO DonationLines(id,donationid,categoryid,quantity) VALUES (?,?,?,?)", list(objs['line']))
                print('line')
            c.execute("COMMIT TRANSACTION")
            print('committed')
            conn.close()   
            logging.info('wrote '+str(len(dons))+' donation(s) into db at '+datetime.datetime.now().strftime("%H:%M:%S, %Y-%m-%d"))
            return True
        except:
            c.execute("ROLLBACK TRANSACTION")
#            for i in range(len(dons)):
#               
               #logging.error("Add into DB failed f:"+dons[i].donor.name["First"]+" l:"+dons[i].donor.name["Last"]+" donated:" +','.join([str(it)+' x '+str(items[i][it]) for it in items[i].keys()])+" on: "+str(times[i]))
           
            conn.close()
            return Exception
    if write==1:
        succ=writefn(inps)
        return succ
    else:
        conn.commit()
        conn.close() 
        return objs
def donationdbClean(cats=[]):#clean up db
    pass
    """
    #checks if names are doubled, updates relevant donation info
    checks for tagged names
    #builds a catmap and checks if everything's consistent
    if functionally different than catmap in db, update all donationlines so they map to the right cats
    eventually, make easily clickable thing for categories not already accounted for
    """
def buildCatmap(base=False,updateold=True):
    #creates category map (if doesn't already exist) - maps old categories to base categories
    bc=['books',
         'furniture',
         'electronics',
         'household',
         'kitchen',
         'clothes',
         'toys',
         'misc.','Dump Fee']
    basecats=dict(zip(bc,range(len(bc))))
    
    cm={'bag of clothes/shoes': 'clothes',
             'box of books': 'books',
             'box of household items': 'household',
             'box of toys': 'toys',
             'box of videos/cds': 'electronics',
             'car donations': 'misc.',
             'clothing': 'clothes',
             'demo': 'misc.',
             'donation': 'misc.',
             'donation house': 'household',
             'dump fee': 'Dump Fee',
             'electronics / appliances':'electronics',
             'jewelry': 'misc.',
             'large appliances': 'electronics',
             'miscellaneous': 'misc.',
             'misc':'misc.',
             'movies/video games/music': 'electronics',
             "tv's/electronics": 'electronics',
             'seasonal':'misc.',
             'support':'misc.',
             'Media-DVD/CD/BLRAY':'electronics',
             'linen':'misc.',
             'linens':'misc.',
             "TV/Electronics":'electronics',
             'shoes':'clothes',
             'appliance':'electronics',
             'crafts':'household'}
    for b in basecats: #
        cm[b]=b
    #categories w number base
    if updateold==True:
        for o in oldcats.keys():
            if str(oldcats[o]) in bc:
                cm[o]=oldcats[o]
            else:
                cm[o]=cm[oldcats[o]]
                
    
    catmap=dict([[str(i).lower(),basecats[str(cm[i])]] for i in cm.keys()]) #gives a dict that maps the 
    
    #if not in cm, map to misc.
    if base==True:
        return catmap,basecats
    else:
        return catmap
def writeCatmap(ret=False):
    catmap,base=buildCatmap(base=True)
    CATS=[]
    cc=0
    for b in base.keys():#list of triples which forms basis for categorymap order
        CATS.append([cc,b,base[b]])
        cc=cc+1
    for c in catmap.keys():
        if c not in base.keys():
            CATS.append([cc,c,catmap[c]])
            cc=cc+1
            
    
    wrongcats=dict(connwrite(dbpath,("SELECT * FROM DonationCategories",)))
    #dict mapping wrongcat to basecat
    ocm=dict([(i,catmap[wrongcats[i]]) if wrongcats[i] in catmap.keys() else (i,catmap['misc.']) for i in wrongcats.keys()])
    
    ww={wrongcats[w]:w for w in wrongcats.keys()}
    upd=[]
    for c in CATS:
         try:#NEWCAT,OLDCAT
             upd.append([c[0],ww[c[1]]])
         except:
             pass
    if ret==True:
        return upd
    for o in CATS:#All that changes here is that the cats point to the same name in catmap instead of donationcategories w a diff index
    
       connwrite(dbpath,("UPDATE OR ROLLBACK DonationLines SET CategoryID = ? WHERE CategoryID =?",(o[0],o[2])))
#  
        
    connwrite(dbpath,("DROP TABLE CategoryMap",))
    connwrite(dbpath,("DROP TABLE DonationCategories",))
    connwrite(dbpath,("CREATE TABLE IF NOT EXISTS CategoryMap(id INTEGER, name TEXT, mapstoid INTEGER,UNIQUE (name))",))
    connwrite(dbpath,('CREATE TABLE IF NOT EXISTS DonationCategories(id INTEGER NOT NULL PRIMARY KEY,name TEXT)',))
    for b in base:
        connwrite(dbpath,("INSERT INTO DonationCategories (id,name) VALUES (?,?)",(base[b],b)))
    
    for m in CATS:    
        connwrite(dbpath,("INSERT INTO CategoryMap (id,name,mapstoid) VALUES (?,?,?)",m))
 
    print('done')
def winprint(file):
    win32api.ShellExecute (
                          0,
                          "print",
                          file,
                      #
                      # If this is None, the default printer will
                      # be used anyway.
                      #
                          '/d:"%s"' % win32print.GetDefaultPrinter (),
                          ".",
                          0
                        )
def expprint(fn):
    im=Image.open(fn)

    printer_name=win32print.GetDefaultPrinter()
    hDC = win32ui.CreateDC ()
    hDC.CreatePrinterDC (printer_name)
    printer_size = hDC.GetDeviceCaps (im.size[0]), hDC.GetDeviceCaps (im.size[1])
    printer_margins = hDC.GetDeviceCaps (0), hDC.GetDeviceCaps (1)


    hDC.StartDoc (fn)
    hDC.StartPage ()
    dib = ImageWin.Dib (im)
    x1=0
    y1=0
    x2 = int ((im.size[0]/1.75) )
    y2 = int ((im.size[1]) )

    dib.draw (hDC.GetHandleOutput (), (x1, y1, x2, y2))
    hDC.EndPage ()
    hDC.EndDoc ()
    hDC.DeleteDC ()
    
"""global variables below here
"""
#webbrowser.open_new(feedbacklink)

#wd=os.path.dirname(os.path.realpath(sys.argv[0])) #gets current working directory for this file
wd=os.getcwd()

logging.basicConfig(filename=wd+r'/Data/docklog.log',level=logging.INFO)
logging.debug('connected to log')

fontpath=wd+r'\Fonts'

dpath=wd+r'\Data'
dbname=r'\donations.db'
#dbname=r'\donations (1).db'
dbpath=dpath+dbname

tokenpath=wd+r'\dockcredentials.json'#credentials to ohworker email

credpath=wd+r'\dockcredentials.json'#credentials to ohworker email
#check if current version is experimental
expdict={True:{'str':'Experimental','file':'OHDock-new'},False:{'str':'Stable','file':'OHDock'}}

curdoc=os.path.realpath(__file__)


oldcats=dict(zip(range(270,282),["misc","toys","clothing","household","books","Media-DVD/CD/BLRAY","furniture","TV/Electronics","shoes","linen","appliance","crafts"]))
daylist=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
#db=path+dbname
#
##threading
#LOCK=threading.Lock()
#recthread=threading.Thread(target=DonationWindow.printfn)
#    t.daemon=True
#    t.start()f


#dockrun()