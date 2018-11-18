__version__='0.2.3'
# -*- coding: utf-8 -*-
"""
TO DO:
    Make combo boxes refresh right - own class?
    Make clear refresh fn in wind for active tag 
    call refresh fn when user finishes editing boxes/selects combo
    
    Better way of handling name conversions
    Guide w/ pics
    category delegates for full list clickability
    fix refill fn & proper window/something for progress bar
    fix checkboxes, header & alignment issues for csv 
    make month clickable&editable thru delegate
    Controller?/custom styles
    Bigger Buttons/More obvious UI
    catch closing without selection/invalid
    "add new product" connect to epos w js???? 
    easy way to add csv into db
    clean up code 
    error handling
    logging
    deal with tag line breaking
    integrate variable pricing better - remove any non variables from epos
    Make caching work more elegantly
    App Connectivity Wireless
    Make more logging!!!
"""

from PyQt5 import QtGui, QtCore,QtSql
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread
from OHLib import *
from PIL import ImageQt, Image, ImageDraw, ImageFont,ImageOps
#from queue import Queue
from time import sleep
import itertools
import csv
import sys
import sqlite3
import pickle #for cache
import code128
import pandas
import datetime
import os 
#import win32print
#import win32api
import webbrowser
import logging
import threading
#Use Protocols????
def dyn_look(obj, dot_attrs):
    attr_list = dot_attrs.split(".")
    while attr_list:
       
        obj = getattr(obj, attr_list[0])
        attr_list.pop(0)
    return obj



    
                #lambda l: self.cpad.configure(qual=self.evar.get
def popup(x):
    pass #make into QT, actually use at points
    #messagebox.showinfo(str(x))
#    popup=Toplevel()
#    popup.wm_title("!")
#    label=ttk.Label(popup,text=str(x))
#    label.pack()
#    B1=ttk.Button(popup,text="OK",command=popup.destroy)
#    B1.pack()
#    popup.mainloop()







"""==================================================================
 GUI FRAMEWORK SPECIFIC GOES HERE   
 """   
def tagrun():
    lock=threading.Lock()
    renderthread=threading.Thread()
    app=0         
    app=QApplication(sys.argv)  
    global stack
    stack=QStackedWidget()
    global itin
    global picin 
    its=ItemsWindow()
    itin=stack.addWidget(its)
    pic=PicWindow()
    
    picin=stack.addWidget(pic)
    layout=QVBoxLayout()
    layout.addWidget(stack)
    stack.setCurrentWidget(its)
    mainthread=windowThread()
    mainthread.run(stack)
    #wind=ItemsWindow()
    #wind.show()
    app.exec_()
class windowThread(QThread):
    def run(self,stack):
        stack.show()
        print('running thread')
        
        
##################

        
class CategoryBox(QComboBox): #modified combobox for categories
    
    selectedChanged = QtCore.pyqtSignal(list)
    def hidePopup(self): #need to overwrite this so that it won't disappear on every click
        self.results = []
        
        for i in range(self.count()):
            if self.itemData(i, QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked:
               self.results.append(self.itemText(i))
        self.selected=self.results
        self.selectedChanged.emit(self.results)
        
        QComboBox.hidePopup(self)
def chkmdl(modl,*args,**kwargs):    
    
    class CheckModel(modl):
        def __init__(self, modl, *args, **kwargs):
            self.modl=modl()
            modl.__init__(self, *args, **kwargs)
            self.checks = {} #Set of category checks
    
        def checkState(self, pindex):
            if pindex not in self.checks.keys(): #if fed index isn't already in our check list:
                self.checks[pindex] = QtCore.Qt.Unchecked #add it as unchecked
            return self.checks[pindex] 
    
        def data(self, index, role=QtCore.Qt.DisplayRole):
            if role == QtCore.Qt.CheckStateRole and index.isValid():  
                return self.checkState(QtCore.QPersistentModelIndex(index))#
            return modl.data(self, index, role)
    
        def setData(self, index, value, role=QtCore.Qt.EditRole):
            if role == QtCore.Qt.CheckStateRole and index.isValid():
                self.checks[QtCore.QPersistentModelIndex(index)] = value 
                return True
            return modl(self, index, value, role)
    
        def flags(self, index):
            fl = modl.flags(self, index) & ~QtCore.Qt.ItemIsSelectable 
            fl |= QtCore.Qt.ItemIsEditable| QtCore.Qt.ItemIsUserCheckable
            return fl
    return CheckModel(modl,*args,**kwargs)
###menu actions here?
def refill(parent):
    d=parent.attinds
    dr=QFileDialog.getExistingDirectoryUrl().path(QtCore.QUrl.FullyDecoded)
    
    dr=dr[1:].replace('/','\\')
    bar=QProgressBar(parent)
    bar.show()
    bar.setMinimum(0)
    bar.setMaximum(parent.modl.rowCount())
    
    for i in range(parent.modl.rowCount()):
        
        td=dict() #all the attributes for this tag
        for a in d.keys():  
            td[a]=parent.modl.data(parent.modl.index(i,d[a]))    
            #str(getattr(self.price,'value'))+'-'+str(getattr(self.barcode,'value'))+'-generated'+str(rn.day)+str(rn.month)+str(rn.year)+'.bmp'
        
        for m in mondict.keys():
            
            
            path = dr+r'\%s\%s'%(str(td['category']).strip(),str(m)+mondict[int(m)])
            if os.path.exists(path): #m
                
                if td['barcode']!='': #ignore non-barcoded
                    try:
                        bcs=[int(float(i.split('-generated')[0].split('-')[1])) for i in os.listdir(path)] #splits on 'generated' then breaks into barcode
                    
                        if int(td['barcode']) in bcs: #if tag's already made
                            print
                            break #breaks to next month
                        else:
                            tag=Pricetag(td,monoverride=m)
                            tag.savetag(root=dr)
                    except: #something went wrong in looking up tags, so break
                        print('broke '+str(i))
                        break
            else:#creates path for this month
              
                tag=Pricetag(td,monoverride=m)
                tag.savetag(root=dr)
        bar.setValue(i+1)
    print('done!')
    bar.hide()
def locatefn(parent,typ):
    print(parent)
    file=parent.choose_file(typ)
    if typ=='db':
        tree=dbtotree(file)
    elif typ=='csv':
        print(file)
        tree=csvtotree(file)
    parent.repopulate(tree)
    
### 
class ItemsWindow(QWidget):
    def __init__(self): 
        
        self.cash=cache(cachepath)
        paths=self.cash.opn('dbpath','csvpath')#checks if there's some saved location for files, changeable prioritization?             
        
        super(ItemsWindow,self).__init__()
        
       
        
        self.layout=QGridLayout()
        vrslbl=QLabel(text='<i>'+'version: '+__version__+'</i>',textFormat=1)
        self.layout.addWidget(vrslbl,10,0)
        self.setLayout(self.layout)
        self.setWindowIcon(QtGui.QIcon(r'C:\Users\V\Python\Opphouse\Visuals\BarcodeMakerIconSmall.png'))
        
        
        s=QScrollArea().setWidget(self.Window())
        self.menubar=QMenuBar(self)
        filemenu=self.menubar.addMenu('File')
        locate=filemenu.addMenu('Locate Product Data')
        dbl=locate.addAction('Locate via .db file')
        dbl.triggered.connect(lambda:locatefn(typ='db',parent=self))
        cvl=locate.addAction('Locate via .csv file')
        cvl.triggered.connect(lambda:locatefn(typ='csv',parent=self))
        rf=filemenu.addAction('Refill Tag Folders')
        rf.triggered.connect(lambda:refill(self))
        #filemenu.addAction('Change Language/Cambiar Idioma')
        
        helpmenu=self.menubar.addMenu('Help!!')
        link=helpmenu.addAction('Bugs/Feedback')
        link.triggered.connect(lambda:webbrowser.open_new(feedbacklink))
       # helpbox=helpmenu.addAction('How do I use this?')
        helpmenu.setToolTip("In Progress!!!")
        
        
        
        if 'dbpath' in paths.keys(): #if the cache already knows dbpath - make more resistant to errors
            self.repopulate(dbtotree(paths['dbpath']))
        elif 'csvpath' in paths.keys():
            self.repopulate(csvtotree(paths['csvpath']))
           
#        self.menu.add_command(label="Submit Feedback/Report a Bug",foreground="blue",command=callback)
#      
#        self.config(menu=self.menubar)
        #webbrowser.open_new(fink)
    def Window(self):
        #make data into some qobject referring to pandas?
        #self.picpage=stack.widget(picin) #gets the page if data transmission needed between, like selected indices
        #print(self.picpage)
        
        self.view=QTableView()
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows) #selects rows
        self.view.setSelectionMode(QAbstractItemView.MultiSelection) #each selection is toggles whether item is in selection - don't need to hold down shift
        #self.view.setSortingEnabled(True)
        
        self.view.setMinimumWidth(400)
        self.view.setMaximumWidth(700)
        
        self.sel=QtCore.QItemSelectionModel()
        self.layout.addWidget(self.view,1,0)
        
        self.catbx=CategoryBox()
        self.catbx.setToolTip("Choose which categories of tags to print")
        
                
        self.catbx.selectedChanged.connect(self.catfn)
        self.layout.addWidget(self.catbx,0,1)
        
        self.des=QPushButton(text='Deselect All')
        self.des.clicked.connect(lambda:self.view.selectionModel().reset()) #make it so this appears and disappears based on selection
        self.des.clicked.connect(self.selectfn)
        self.des.setHidden(True) 
        self.layout.addWidget(self.des,2,1)
        
        self.csv=QPushButton(text="Locate CSV")
        self.layout.addWidget(self.csv,3,0)
        self.csv.clicked.connect(lambda:locatefn(typ='csv',parent=self))#connect to openfilewindow -> parse somehow
        
        self.db=QPushButton(text="Locate DB")
        self.layout.addWidget(self.db,2,0)
        self.db.clicked.connect(lambda:locatefn(typ='db',parent=self))#connect to openfilewindow -> parse somehow
  
        self.sw=QPushButton("Print Tags") #make only appear if tags are selected,
        self.sw.setHidden(True)
        self.sw.clicked.connect(self.switchfn)
        self.sw.setFixedHeight(80)
        self.layout.addWidget(self.sw,1,1)
        self.sw.sizePolicy().setRetainSizeWhenHidden(True)
        
    def choose_file(self,typ='csv'):
        temp = QFileDialog.getOpenFileName(filter = typ+" files (*."+typ+")")
        self.filename=temp
        if typ=='db':
            pass
        return self.filename[0]
    def catfn(self):
        
        if len(self.catbx.selected)!=0:
            self.regex=self.catbx.selected[0]
            for i in range(len(self.catbx.selected)):
                try:
                    self.regex=self.regex+'|'+self.catbx.selected[i+1]
                except:
                    pass
            self.proxy.setFilterRegExp(self.regex)
    @property
    def inds(self): #row indexes
        return [i for i in self.view.selectionModel().selectedRows()]
    def selectfn(self): #
        if len(self.inds)==0: #if number of selected items is 0
            self.sw.setHidden(True)
            self.des.setHidden(True)
            pass #make des and continue button disapear, popup some sort of label text to guide user along
        else: #number selected is not 0
            self.sw.setHidden(False)
            self.des.setHidden(False)
            pass #make des and continue appear
    def switchfn(self): #everything that happens when page switches to pricetag page
        stack.widget(picin).inds=self.inds
        
        stack.widget(picin).calltag()
        stack.setCurrentIndex(picin) #actually switches the page 
        #print(self.inds)
        #self.inds
    def populate(self,d):
        #Can be done using table w delegate checkboxes?
        #different modls if connected to db or not?
        #handling models:
        self.attinds=dict()
        if type(d)==type(QtSql.QSqlDatabase()): #if fed connection
            conn=d
            conn.open()
            #categories - do as tree through qproxymodel?http://www.qtcentre.org/threads/12064-QSql%2AModel-QTreeView-make-a-tree
            self.catq=QtSql.QSqlQuery(conn) 
            self.catq.exec("SELECT name FROM categories")
            self.catmo=chkmdl(QtSql.QSqlQueryModel)
            
            self.catmo.setQuery(self.catq)
            
            #self.catmo.setHeaderData('Categories')
            #table
            self.qry=QtSql.QSqlQuery(conn)
            self.qtxt="SELECT products.Price,products.Name,products.Barcode,categories.name FROM products INNER JOIN categories WHERE products.CategoryIndex=categories.id"
            self.attinds=dict([[i,dbdict[i]['index']] for i in dbdict])
            
            self.qry.exec(self.qtxt)
            try: del self.modl
            except: pass
            self.modl=QtSql.QSqlQueryModel()  
            self.modl.setQuery(self.qry)
            
            
            if self.modl.rowCount()!=0: #if all this worked to add data to model, save filename
                
                self.cash.sv(dbpath=d.databaseName())
            else:#if this db file didn't have the right formatting
                pass 
            conn.close()
        elif type(d)==type(pandas.DataFrame()): #fed csv tree
            try:del self.modl
            except: pass
            self.modl=self.CSVTableModel(data=d,parent=self)
            atts={"price","description","category","barcode"}
            
            self.catmo=chkmdl(QtCore.QStringListModel)
            self.catmo.setStringList(list(d[csvdict['category']['label']].fillna('None').unique()))
            
            for i in atts:
                self.attinds[i]=list(self.modl.tree).index(csvdict[i]['label'])
            if self.modl.rowCount()!=0: #if all this worked to add data to model, save filename
                print(self.modl.path)
                self.cash.sv(csvpath=self.modl.path)
                
        else: ValueError
        
        #handling views:
#        self.catview=QListView()
#        self.catview.setModel(self.catmo)
#        self.catbx.setView(self.catview)
        
        self.catbx.setModel(self.catmo)
        self.proxy=QtCore.QSortFilterProxyModel()
        self.proxy.setSourceModel(self.modl)
        #self.view.setHorizontalHeader(['barcode','description','price'])
        self.view.setModel(self.proxy)
        
        self.view.setAlternatingRowColors(True)
        self.view.SelectionMode(2)
        self.vieworder={'barcode':0,'price':1,'description':2,'category':None}
        self.view.setSelectionModel(self.sel)
        self.view.selectionModel().selectionChanged.connect(self.selectfn)
        self.sel.setModel(self.proxy)
        try: #sets inds if model is loaded
            
            for i in self.attinds:
                self.view.showColumn(self.attinds[i])
                #self.proxy.setHeaderData(self.attinds[i],i)
                
            self.proxy.setFilterKeyColumn(self.attinds['category'])
            self.view.hideColumn(self.attinds['category'])
        except:
            pass
        #   self.view.clicked.connect(lambda:print())
        
        self.selectlist=dict()
        x=self.modl.columnCount()
        y=self.modl.rowCount()
        
        #print(x,y)
        for ii in range(y):
            for jj in range(x):
                #QStyleOptionView
                self.selectlist[ii]=QCheckBox()
                #print(self.view.indexAt(ii,jj,))
    def repopulate(self,d=pandas.DataFrame()):
        #self.tbl.clear
        self.populate(d)
    class CSVTableModel(QtCore.QAbstractTableModel):    
        def __init__(self,path=None,data=None,*args,**kw):   
            super(ItemsWindow.CSVTableModel,self).__init__(*args,**kw)
            if path is not None and data is None: #path provided w/o data
                self.path=path
                self.tree=csvtotree(self.path)
            elif data is not None: #data provided 
                self.tree=data
                self.path=data.name
                
        def rowCount(self,index=0):
            return len(self.tree)
        def columnCount(self,index=0):
            return len(self.tree.columns)
        def data(self,index,role=QtCore.Qt.DisplayRole):
            return self.tree[self.tree.columns[index.column()]][index.row()]
        def headerData(self,section,orientation=QtCore.Qt.Orientation,role=QtCore.Qt.DisplayRole): #not working
            
            if orientation==QtCore.Qt.Horizontal:
                
                if section in self.parent().attinds.values(): 
                    
                    a=list(self.parent().attinds.values()).index(section) #reverses dict, basically
                    b=list(self.parent().attinds.keys())[a] 
                   
                    return b
                else:
                    return None
            else: return section
#=========================================PageBreak=========================================#


class PicWindow(QWidget):
    def __init__(self): #need controller?
        super(PicWindow,self).__init__()
        self.layout=QGridLayout()
        vrslbl=QLabel(text='<i>'+'version: '+__version__+'</i>',textFormat=1)
        self.layout.addWidget(vrslbl,15,0)
        self.setLayout(self.layout)
        
        s=QScrollArea().setWidget(self.Window())
        
    #show pricetag of one(s) selected, rudimentary controls for details 
    #(textsize,checkbox for if_variable,maybe position "gamepad" controller?)
    #Maybe present simple "stamps" to put on? 
    
    class updateThread(QThread):
        def run(self,updatefn):
            
            updatefn()
        def isRunning(self):
            QThread.isRunning(self)
            
    def UpdateDecorator(updatefn): #handles update in separate thread so as to not break program display
        def threader(self):
            t=self.updateThread()
            
            t.run(lambda:updatefn(self))
            while t.isRunning():#makes sure pixmap is set after image is rendered
                time.sleep(.01)
           
            self.label.setPixmap(qtim) #comment this line out if the tag resolution is making the program crash, hopefully temp fix!!!
            #save and print should work fine
        return threader
    
    @UpdateDecorator
    def Updatetag(self): #updates tag, interfaced when tag is first called, elements r changed, or switched between tags
            tag=self.taglist[self.actv]
            
            global qtim
            qtim=QtGui.QPixmap.fromImage(ImageQt.ImageQt(tag.render()))
            
            
    def Window(self):   
        self.actv=0
        #self.actv=IntVar(value=0) #which tag is actively shown
        
        self.evar="barcode" #active attribute to be edited
        self.listpage=stack.widget(itin) #other page obj
        
        #self.scr=controller.frames[ScrollPage] #if need to refer to attributes on that page - which i do
        
           
        self.tags=[] #keeps the tag objects, which can be edited and told to render without having to redefine 
        #check how many are in list for framing
        #allocate positions for frame(s)
        #c=Canvas(self,width=500,height=353)
      
        
        self.label=QLabel('test') 
        self.layout.addWidget(self.label,3,3,3,3)
        #self.label=Label(self,relief=RIDGE,borderwidth=20)
        #self.label.grid(row=3,column=3,columnspan=3,rowspan=8)
            
        #self.ent=QLineEdit()
        #self.layout.addWidget(self.ent,0,1)
        
        #QFontComboBox to choose font
        
        self.cdt=QPushButton(text="<< Choose Different Tags")
        self.layout.addWidget(self.cdt,6,0) 
        self.cdt.clicked.connect(lambda:stack.setCurrentIndex(itin))
        #self.sb=ttk.Button(self,text="<< Choose Different Tags",command=lambda: controller.show_frame(ScrollPage))
        #self.sb.grid(column=0,row=3)
        
        inps={'int':QtGui.QIntValidator(1,99999),'$':QtGui.QDoubleValidator(0,99999,2),'%':QtGui.QDoubleValidator(0,100,2)}
        self.tag=[]
        self.combotyp=None#keeps track of what combo is selected in the box
        def comboselfn(combo):
            def comboinpfn(amount,string):#
                edittyp=combos[self.combotyp]['str']
                for i in range(len(self.comboinps)):
                    edittyp=edittyp.replace('['+str(i)+']',str(self.comboinps[i].text()))
                self.taglist[self.actv].combo.value=edittyp     
                self.Updatetag()
                
            if self.comboinp.layout() is not None:#deletes old lineedits
             
                while self.comboinp.layout().count():#goes thru each member of the layout and deletes it 
                    it=self.comboinp.layout().takeAt(0)
                    wid=it.widget()
                    if wid is not None:
                        wid.deleteLater()
#                        
            self.combotyp=combo 
            self.taglist[self.actv].combo.value=combos[combo]['str']
           
            self.comboinps=[]
            for i in range(len(combos[combo]['typs'])):
                c=combos[combo]['typs']
                l=QLineEdit(self.comboinp)
                self.comboinps.append(l)
                l.setObjectName(str(i))
                l.setPlaceholderText(c[i])
                l.setValidator(inps[c[i]])
                l.editingFinished.connect(lambda i=i: comboinpfn(l.text(),i))
                self.comboinp.layout().addWidget(l)
            
            self.comboinp.update()
            self.Updatetag()
            
        self.comboinp=QGroupBox()
        self.comboinp.setLayout(QVBoxLayout())
        self.layout.addWidget(self.comboinp,1,2)
        self.combobox=QComboBox()
        self.combobox.addItems(combos.keys())
        self.combobox.currentIndexChanged[str].connect(lambda c:comboselfn(c))
        self.layout.addWidget(self.combobox,0,2)
        
        def changetag(ind):
            self.actv=ind
            self.Updatetag()
            self.tag=self.taglist[ind]
            if self.actv>(len(self.inds)-2):
                self.nt.setHidden(True)
                #self.layout.removeWidget(self.nt)
            else:
                self.nt.setHidden(False)
               # self.layout.addWidget(self.nt,4,6)
                
            if self.actv<1:
                self.pt.setHidden(True)
            else:
                self.pt.setHidden(False)
                #s
            
        #next/prev tag buttons
        
        self.nt=QPushButton(text="Next Tag")
        self.nt.clicked.connect(lambda:changetag(self.actv+1))

        self.pt=QPushButton(text="Previous Tag")
        self.pt.clicked.connect(lambda:changetag(self.actv-1))
        
        self.layout.addWidget(self.nt,4,6)
        self.layout.addWidget(self.pt,4,0)
        self.nt.setHidden(True)
        self.pt.setHidden(True)
        self.nt.sizePolicy().setRetainSizeWhenHidden(True)#these aren't working
        self.pt.sizePolicy().setRetainSizeWhenHidden(True)
        self.svall=False
        self.svbx=QCheckBox(text="Save All?") #may not be necessary?
        #self.layout.addWidget(self.svbx)
        #self.svbx=ttk.Checkbutton(self,text="Save all?",variable=self.svall)
        #self.svbx.grid(sticky="w")
        
         #self.undtxt=BooleanVar(value=False)
  #      self.undbx=ttk.Checkbutton(self,text="Undertext?",variable=defpand['barcode']['underbar'])
   #     self.undbx.grid(sticky="w")
        
        self.svbtn=QPushButton(text="Save Tag")
        self.svbtn.clicked.connect(lambda: savetags(self.taglist,pr=0))
        self.layout.addWidget(self.svbtn)
      #self.sv=ttk.Button(self,text="Save Tag",command=lambda: savetags(self.taglist))
        self.pbtn=QPushButton(text="Print Tag")
        self.layout.addWidget(self.pbtn)
        self.pbtn.clicked.connect(lambda: savetags(self.taglist,pr=1))
            
        #self.pb=ttk.Button(self,text="Print Tag",command=lambda: savetags(self.taglist,pr=1))
        #v=StringVar(value='stck')
        self.stckstyl=QPushButton(text="Sticker")
        self.stckstyl.setCheckable(True)
        self.stckstyl.setChecked(True)
        self.stckstyl.setFlat(True)
        self.stckstyl.setObjectName("stck")
   
        #need to both update variables and calltags
        #self.stckstyl.bind("<Leave>",lambda q:calltag())
        self.shtstyl=QPushButton(text="Sheet")
        self.shtstyl.setObjectName("sht")
        self.shtstyl.setCheckable(True)
        self.shtstyl.setFlat(True)
        self.grp=QGroupBox()
        self.boxstyl=QHBoxLayout()
        self.grp.setFlat(True)
        self.grp.setLayout(self.boxstyl)
        self.boxstyl.addWidget(self.stckstyl)
        self.boxstyl.addWidget(self.shtstyl)
        self.layout.addWidget(self.grp,1,4)
        
        self.box=QButtonGroup()
        self.box.addButton(self.stckstyl)
        self.box.addButton(self.shtstyl)
        self.box.setExclusive(True)
        #self.box.buttonToggled(self.stckstyl,self.calltag
        self.box.buttonToggled.connect(lambda: self.calltag())
        #self.shtstyl=Radiobutton(self,text="Sheet",indicatoron=0,variable=v,value="sht")
        #self.shtstyl.grid(column=5,row=1)
        #self.shtstyl.bind("<Leave>",lambda q:calltag())
        
        tb=QPushButton(text="update tag")
        #self.layout.addWidget(tb,1,2)
        #tb=ttk.Button(self,text="Update tag",command=calltag)
        #tb.grid(row=1,column=2)   
        def savetags(taglist,pr=0):
            
                    
            if self.svall==True:
                printlist=taglist
            else:
                printlist=taglist[self.actv]
            
            for i in taglist:
                i.savetag(pr=pr)
                
    def calltag(self): #first start of tagobj
        self.layout.addWidget(self.svbtn,5,6) #add save and print buttons
        self.layout.addWidget(self.pbtn,6,6)
        #self.sv.grid(column=6,row=5)
        #self.pb.grid(column=6,row=6)
        self.actv=0
        self.taglist=[]
        typ=self.box.checkedButton().objectName()
      
        
        for i in self.inds:
            #data
            d=self.listpage.attinds
            data=dict()
            for a in d.keys():
                
                
                data[a]=self.listpage.proxy.data(self.listpage.proxy.index(i.row(),d[a])) #gets data at specified index
                
            self.taglist.append(Pricetag(data,typ=typ))
        
        if len(self.inds)>1: #handling buttons to switch between tags
            if (len(self.inds))>1:
                self.nt.setHidden(False)
               #self.nt.grid(column=6,row=4) #inconvenient, change somehow
            else:
                #self.nt.grid_forget()
                self.nt.setHidden(True)
        print(self.actv)
        print(self.taglist)
        self.tag=self.taglist[self.actv] #active tag
        self.Updatetag()
      ##  self.chkvar=ttk.Checkbutton(self,text="Variable Price", variable=self.tag.price.variable)
           # self.chkvar.grid(row=3,column=1)
            # delete old cpad if exists
#            self.cpad=Controlpad(self)
#            self.cpad.grid(row=4,column=0)
#            self.cpad.bind("<ButtonRelease-1>",lambda q: Updatetag(self)) #Button-1 doesn't like it for some reason 
#            #print(self.cpad.bindtags.)
            #self.cpad.bind("<Leave>",lambda q: Updatetag(self.tag))
    
        editstrs={"barcode","month","category","price","blurb"} #what attribute is being edited w pad - still working on it
        self.edict=dict()
        self.ebutts=[]
        
        ee=0
#            for e in editstrs: #control buttons, low priority rn
#                if e in self.tag.__dict__.keys():
#                    #have controlpad hooked up to this somehow - respawn on click of radios?
#                    #make thing highlighted on label?
#                    
#                    self.edict[e]=[self.tag.__dict__[e]]
#                    self.ebutts.append(Radiobutton(self,text=e,variable=self.evar,value=e))
#                   
#                    #self.ebutts[-1].bind("<Leave>",updatecont) #buttonrelease would show last time it updated (the variable gets set after click i guess?)
#                    
#                    self.ebutts[-1].grid(row=ee+2,column=1)
#                    ee=ee+1
##Reimplement controller at some point?
#
#
#


"""General Classes



"""
class Pricetag():
    def __init__(self,d,typ='stck',monoverride=None): #d is dict with relevant info - default res is 100 so if different gets shifted by ratio
        self.dicts={'stck':tagstyle,'sht':furnstyle}
        #datadict also influenced by user action - db or csv
        self.type=typ #do st(i)ck(er) or sh(ee)t
        tagdict=pandas.concat([datadict,self.dicts[self.type]])
        self.res=tagdict['image']['res']
        self.imsize=tuple([round(self.res*tagdict['image']['imsize'][ii]/tagdict['image']['nxy'][ii]) for ii in [0,1]])
       
        for i in tagdict.keys(): #for each  element in the dict
            setattr(self,i,self.attribute()) #may not work?
            attr=getattr(self,i)
            if pandas.notna(tagdict[i]['label']): #all attributes which get info from table  
                setattr(attr,'value',d[i]) #change value
            if 'text' in tagdict.index: #if this chosen dictionary uses text
                if pandas.notna(tagdict[i]['text']): #if there's some specific text saved in this element
                    setattr(attr,'value',tagdict[i]['text'])
            
            if 'c' in tagdict[i].dropna().keys(): #have to change up here bc can't check isna for 2-member list
                setattr(attr,'pos',[self.imsize[k]*tagdict[i]['c'][k] for k in [0,1]])#position of center of attribute

            if pandas.notna(tagdict[i]['font']): #make sub of text?
                setattr(attr,'font',ImageFont.truetype(tagdict[i]['font'],round(tagdict[i]['size']*self.res/100)))
                
            
        x,y=self.imsize #shorthand 
        if monoverride==None:
            setattr(self.month,'value',datetime.date.today().month)
        else:
            setattr(self.month,'value',monoverride)
        if self.barcode.value!='': #BARCODE PARSER: if not blank, figure out code and set barcode 
            speccodes={'C':'combo','V':'variable'}
            #combos: X for $, X for (price of) Y, % Discount, Spend $ Save %, Spend $ Save $, Points (Bonus), Points (Multiple)
            bar=self.barcode.value
            splitbar=[''.join(g) for _,g in itertools.groupby(bar,str.isalpha)] #splits incoming barcode string by integers vs. letters
            self.spec=self.attribute()
            if len(splitbar)==1:
                setattr(self.underbar,'value',int(self.barcode.value))
                self.spec.types=[]
            elif len(splitbar)>1:#if it was able to split by alphabet, then there's a special code in the barcode
                
                self.spec.value=splitbar[-1] #do smth here to make sure it doesn't break temp
                if splitbar[-1] in speccodes.keys():#temp make sure can handle multiple codes
                    self.spec.types=[]
                    for i in splitbar[-1]:
                        self.spec.types.append(speccodes[i])
                        
                setattr(self.underbar,'value',self.barcode.value)
                    
      
    class attribute(): #dummy class to be able to give attributes to at will
        
        pass
        
    
        
        #self.stamps
        
        
    def render(self):
        #logging.INFO('rendering '+str(self.barcode.value))
        
        refdict=self.dicts[self.type] 
        self.tag = Image.new('RGB',self.imsize,color="White")
        self.dr=ImageDraw.Draw(self.tag)
        if self.barcode.value!='':
            
            bar=code128.image(self.barcode.value,thickness=round(self.res/100*refdict['barcode']['shape'][0]),height=round(self.res/100*refdict['barcode']['shape'][1]))
            bar=bar.convert('RGB') #convert to RGB just in case
            bar=bar.rotate(refdict['barcode']['rot'],expand=1) 
            #paste barcode onto canvas
            barbox=[round(dyn_look(self,"barcode.pos")[0]),round(dyn_look(self,"barcode.pos")[1]),0,0]
            barbox[2]=barbox[0]+bar.size[0]
            barbox[3]=barbox[1]+bar.size[1]
            self.tag.paste(bar,barbox)
        
        #go through all the ones that have font defined and make that text
        for attrs in refdict.T['font'].dropna().keys():
            attr=getattr(self,attrs) 
            if str(attrs)=='combo':
                if 'combo' in self.spec.types: #if this barcode has C in it, then allow the combo value to be set from the window
                    try:
                        print(self.combo.value)
                        
                    except:
                        print('no combo set')
                else:#not in barcode, nothing happens on tag 
                  self.combo.value=''
                    
                
            if str(attrs)=='underbar':
                if refdict['barcode']['underbar']==True and self.barcode.value!='': #if underbar is shown for this tag style
                
                    attr.pos=[round((barbox[2]+barbox[0])/2),round(barbox[3]+self.res/100*refdict['underbar']['underdist'])]
                    
                    #print('set'+str(self.underbar.pos))
                else:
                    #print('broke')
                    break
            elif str(attrs)=='price': #puts price in right format, this is rly thrown together needs to b better (only changes if tag is actualized)
                try:#if it can be turned into a float make it into dollars
                    setattr(attr,'value','$%.2f'%float(getattr(attr,'value')))
                except ValueError: #else it's already been done
                    pass
                    
             
            attag=Image.new('L',self.imsize,color="White")
            d=ImageDraw.Draw(attag)
            #print(attrs) #useful for debugging 
            try:
                
                attsize=ImageDraw.ImageDraw.multiline_textsize(d,text=str(attr.value), font=getattr(attr,"font"))
                if attsize>self.imsize:
                   #attr.value=str(attr.value.split(' ')
                    #attsize=ImageDraw.ImageDraw.multiline_textsize(d,text=str(attr.value), ffont=getattr(attr,"font"))
                    print('too big'+str(attsize))
                
                variableprice=True #need to include varprice from csv
                
                if attrs=='price' and self.price.value=="$0.00" and variableprice: 
                        attsize=ImageDraw.ImageDraw.multiline_textsize(d,text='$__.00', font=getattr(attr,"font"))
                        aftsize=ImageDraw.ImageDraw.textsize(d,text='.00', font=getattr(attr,"font"))  
                        dolsize=ImageDraw.ImageDraw.textsize(d,text='$', font=getattr(attr,"font")) 
                        d.line( (dolsize[0],attsize[1],attsize[0]-aftsize[0],attsize[1]),width=10)
                        d.text([0,0],text='$__.00',font=getattr(attr,"font"))
                else:
                    d.multiline_text([0,0],text=str(getattr(attr,'value')),font=getattr(attr,"font"))
                
                attbox=[0,0]
                attbox.append(attbox[0]+attsize[0])
                attbox.append(attbox[1]+attsize[1])
                box=[round(dyn_look(attr,"pos")[i]-attsize[i]/2) for i in [0,1]]
                box.append(box[0]+attsize[0])
                box.append(box[1]+attsize[1])
               
                self.tag.paste(attag.crop(attbox),box,mask=ImageOps.invert(attag.crop(attbox)))
            except:
                pass
            # self.dr.text([dyn_look(self,"month.pos")[i].get() for i in [0,1]],str(self.month.get()),0,font=dyn_look(self,"month.font"))           
        
        return self.tag
    def sheetify(self):
        
        refdict=self.dicts[self.type]
        lw=3 #linewidth      
        try: #make
            self.tag
        except NameError:
            self.render()
        sheetsize=(round(self.res*8.5),round(self.res*11.0))
        self.nx,self.ny=refdict['image']['nxy']   
        shtbox=(0,0,round(sheetsize[0]/self.nx),round(sheetsize[1]/self.ny))
        sheet=Image.new('RGB',sheetsize,color='white')
        drsh=ImageDraw.Draw(sheet)
        for i in range(self.nx): 
            for j in range(self.ny):
                sheet.paste(self.tag,[round(x) for x in [shtbox[0]+i*shtbox[2],shtbox[1]+j*shtbox[3],shtbox[0]+i*shtbox[2]+self.tag.size[0],shtbox[1]+j*shtbox[3]+self.tag.size[1]]])
                
                drsh.line( (0,j*sheetsize[1]/self.ny,sheetsize[0],j*sheetsize[1]/self.ny), fill=0,width=lw) #horizontals
            drsh.line( (i*sheetsize[0]/self.nx,0,i*sheetsize[0]/self.nx,sheetsize[1]), fill=0,width=lw) #vertical
        return sheet
    def savetag(self,pr=0,root=None):
        """FOLDER STRUCTURE
        |>Category
        |->{Sub-Category}
        |-->Sheet Tags
        |-->Sticker Tags
        |--->Months
        """
        mon=getattr(self.month,'value')
        if root==None:
            if pr==0:#if not printing then save in custom directory
                
                dr=QFileDialog.getExistingDirectoryUrl().path(QtCore.QUrl.FullyDecoded)
    
                tagfolder=dr[1:].replace('/','\\')
            else: tagfolder=wd+r'\temp'# else just temp?
        else: tagfolder=root
        if self.type=='stck':
            newpath = tagfolder+r'\%s\%s'%(str(getattr(self.category,'value')).strip(),str(mon)+mondict[int(mon)]) #makes folders of categorys and months
            im=self.render()
        if self.type=='sht':
            newpath=tagfolder+r'\%s\Sheets'%(getattr(self.category,'value').strip())
            im=self.sheetify()
        newpath=newpath.replace('/','-') #gets rid of anything harmful to OS path reader
        rn=datetime.date.today() 
        
        if not os.path.exists(newpath): #make directory if doesn't already exist
            os.makedirs(newpath)
        frmt='png'
        filename=newpath+'\\'+str(getattr(self.price,'value'))+'-'+str(getattr(self.barcode,'value'))+'-generated'+str(rn.day)+str(rn.month)+str(rn.year)+'.'+frmt
        
        im.save(filename,format=frmt)
       # print("saved!")
        if pr==1:#make this work with svall
           # if self.svall==False:
                print('printing')
                win32api.ShellExecute (
                  0,
                  "print",
                  filename,
                  #
                  # If this is None, the default printer will
                  # be used anyway.
                  #
                  '/d:"%s"' % win32print.GetDefaultPrinter (),
                  ".",
                  0
                )


"""
DATABASE/CACHE/CSV STUFF HERE
"""        
class cache(): #saves & allocates data for quick booting, such as: Datapath
    def __init__(self,path,filename=r"\cache",**kw):
        self.checkcreate(kw)
        self.obj=dict()
        self.fn=path+filename #filename string
        
        if self.check(): #if cache already exists
            self.opn()
            #want t
            #for a in args: #make variables for each arg?
        else:
            self.sv()
       
            
            
    def check(self): #checks if cache file already exists
        if os.path.isfile(self.fn):
            
            return True
        
        else:
            return False
        
        
    def opn(self,*kws):
        self.data=pickle.load(open(self.fn,'rb'))
        if len(kws)!=0:
            lst=dict()
            for a in kws:
                if a in self.data.keys():
                    lst[a]=self.data[a]
            return lst
        return self.data
    def sv(self,**kw): #checkcreate needed in all fns interfaceable to from other sections
        self.checkcreate(kw) 
        pickle.dump(self.obj,open(self.fn,'wb'))
        
    def createobj(self,kw):
        self.obj=dict()
        #print('made obj')
        for k,v in kw.items():
            self.obj[k]=v
    def checkcreate(self,kw): #function to be used as wrapper?, if function called has kw args then automatically creates obj  
        if len(kw.keys())!=0:
            self.createobj(kw)
def csvtotree(path):
    dp=csvdict
    cats=dp.T['label'].dropna() #categories of interest
    cv=pandas.read_csv(path)
    data=cv[[i for i in cats.values]] #return columns of interest
    
    data[dp['price']['label']]=[str('$%3.2f'%float(i)) for i in data[dp['price']['label']]]
    
    x=data[dp['barcode']['label']]
    data[dp['barcode']['label']]=[i if pandas.notna(i) else '' for i in x]  
    
    data.name=path
    return data

#Don't need immediately, helpful to parse csv file dld from epos onto the db
#def treetodb(data,dbname='products.db'):
#    #get into right format before starting w sql stuff
#    #might b difficult w checking?
#    conn=sqlite3.connect(dbname)
#    c=conn.cursor()    
#    try:
#        c.execute("BEGIN")        
#        #id,category
#        c.execute("COMMIT")
#        conn
#    except sql.Error:
#        c.execute("ROLLBACK")
#    #create tables if dont exist
#    #make sure to use dbFilter!!
#    conn.close()
    
def dbtotree(dbname): #since everything should already be formatted in here, can just select on a join
    conn=QtSql.QSqlDatabase('QSQLITE')
    conn.addDatabase('QSQLITE')
    conn.setDatabaseName(dbname)
    if not(conn.isValid()): 
        print('connection failed :(')
        return ConnectionError
    else:           
        
        return conn
#-----------------------------------GLOBAL STUFF--------------------------------------#
logging.basicConfig(filename='Barcode.Log',level=logging.DEBUG)
data=pandas.DataFrame()
mondict={1:"jan",2:"feb",3:'mar',4:"apr",5:"may",6:"jun",7:"jul",8:"aug",9:"sep",10:"oct",11:"nov",12:"dec"}
rainbow=["red","orange","yellow",'#87FC4C',"cyan","#c94df9"]
colorlist=rainbow

#dicts necessary to get info from csv/db files - non-editable
#'label': column name, 'index': column index (if applicable)
csvdict=pandas.DataFrame({'description':{'label':'Name','index':2}, 
         'price':{'label':'Sale Price  (Exc. Tax)','index':3,"variable":False},
         'barcode':{'label':'Barcode','index':0},
         'category':{'label':'Category','index':1}})
dbdict=pandas.DataFrame({'description':{'label':'Name','table':'products','index':1},
                         'price':{'label':'price','table':'products','index':0},
                         'barcode':{'label':'barcode','table':'products','index':2},
                         'category':{'label':'name','table':'categories','index':3}})
    
datadict=dbdict
    
#Sources for style data - what is on what tag and where
tagstyle=pandas.DataFrame({'image':{'imsize':(5,3.53),'nxy':(1,1),'res':80},
         'description':{'c':[.5,1/8],'size':60,'font':'timesbd.ttf'}, 
         'price':{'c':[.5,3/8],"font":"timesbd.ttf",'size':120},
         'barcode':{'c':[-.05,.65],'rot':0,'underbar':True,'shape':[5,100]},
         'underbar':{'font':'MINI 7 Bold.ttf','underdist':10,'size':20},
         'month':{'c':[.95,.9],"font":"timesbd.ttf","size":40},
         'combo':{'c':[.5,.6],'font':'timesbd.ttf','size':20,'rot':20}})   
   #styles 
furnstyle=pandas.DataFrame({'image':{'imsize':(8.5,11),'nxy':(2,5),'res':150},
         'description':{'c':[.15,4.5/8],'size':20,'font':'timesbd.ttf','text':'Description:'}, 
         'price':{'c':[.5,3/8],"font":"timesbd.ttf",'size':80},
         'barcode':{'c':[.8,.1],'underbar':False,'rot':90,'shape':[2,30]},
         'underbar':{'font':'MINI 7 Bold.ttf','underdist':10,'size':20},
         'month':{'c':[.95,.9],"font":"timesbd.ttf","size":10},
         'blurb':{'c':[0.5,.1],"font":"timesbd.ttf","size":15,'text':'** Items must be picked up before 6pm on the \n  day of purchase. No Exceptions. Thank You! **'},
         'combo':{'c':[.5,.6],'font':'timesbd.ttf','size':15}})

    
    
combos= {'X for $Y':{'typs':['int','$'],'str':'Buy [0] for $[1]'}, 
                 'X for price of Y':{'typs':['int','int'], 'str':'Buy [0] for the price of [1]'},
                 'X% Discount':{'typs':['%'],'str':'[0]% Discount'}, 
                 'Spend $X Save %Y':{'typs':['$','%'],'str':'Spend $[0] on other items, \n get a [1]% discount on this item'},
                 'Spend $X Save $Y':{'typs':['$','$'],'str':'Spend $[0] on other items, \n get a $[1] discount on this item'},
                 'Points (Bonus)':{'typs':['int'], 'str':'Get [0] Bonus Points!'},
                 'Points (Multiple)':{'typs':['int'],'str':'Get [0] Multiple Points! (DONT USE)'}}
defpand=pandas.concat([tagstyle,datadict]) #puts both into one easily accessible list, can change between tag and furnstyles easily without redundantly defining everything in datadict
#c = center of element in % of tag size

wd=os.path.dirname(os.path.realpath(sys.argv[0])) #gets current working directory for this file
cachepath=wd+'\Data'

#tagrun()