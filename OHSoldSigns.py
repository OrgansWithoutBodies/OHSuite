###
#IMPORTS - outside scripts to be used in this file. anything not declared with "import" can't be accessed from this file. 
from PIL import Image, ImageDraw, ImageFont#Python's Image Library 
import os #used to save & load files
import random #random number generator

###
#TEXT DEFINITIONS
#Text:(ratio of location on slip) - each different variable has a different font  & size

#BACK
backblurb={"Once you, the customer, have purchased an item, you are fully responsible for it. \nIf you choose to leave the item and return for it please attach this sign to it until \nyou return. Items must be picked up the same day they are purchased unless arrangements \nfor delivery through the store are made. By signing this form, you the customer \nacknowledge that Opportunity House is not responsible for any damage, re-sell, \nor loss of an item once it has been purchased, and NO REFUNDS will be given. \nDue to the minimum floor/storage space, of your item is left after close \nof the purchase date the store reserves the right to re-sell the item.":(.5,.3)}
backmgmt={"Thank you for your cooperation \nManagement":(.23,.7)}
fieldcorn=(.4,.8)
backfields={"CUSTOMER NAME:":fieldcorn,"CUSTOMER SIGNATURE":tuple(map(sum,zip(fieldcorn,(0,.05)))),"PHONE #":tuple(map(sum,zip(fieldcorn,(0,.1)))), "DATE":tuple(map(sum,zip(fieldcorn,(.3,.1))))}
            
            
#FRONT
fs={"SOLD":(.5,.25)}
fyn={"YES":(.35,.75),"NO":(.5,.75)}
frontbtm={"*Please attach receipt if paid*":(.5,.85),"*All items must be picked up by end of day*":(.5,.95)}
frontfields={"Date:":(.5,.05),'Cashier Initials:':(.25,.6),'Customer Initials:':(.65,.6),'Paid:':(.25,.75)}

lblloc={'':(.1,.1)}

###
wd=os.getcwd()#folder script is stored in, used as relative point at which to save

#### 
#FUNCTIONS
#
def soldTag(res=100, n=(2,6),lbl=None,side='front'):
    tagsize=(round(res*8.5/n[0]),round(res*11.0/n[1]))    
    tag=Image.new('L',tagsize,color="white")
    dtag=ImageDraw.Draw(tag)
    lbltxt={str(lbl):lblloc['']}
    def centertext(d,font,justify='center',line=0,autopar=False):        
      
        for string in d.keys():
            locrat=d[string]
            attsize=ImageDraw.ImageDraw.multiline_textsize(dtag,text=string, font=font)

            if justify=='center':
                justamt=[.5*i for i in attsize]
            elif justify=='left':
                justamt=(attsize[0]/2,0)
            dtag.multiline_text([round(tagsize[i]*locrat[i]-justamt[i]) for i in range(2)],string,anchor='center',font=font)#takes the size of the tag, multiplies it by location ratio, then subtracts pixelsize of text - needed bc default action of text is to go from top-left corner, this ends up doing from the center
            #add line here
    ubuntum=os.path.join(wd,"Fonts","ubuntu","Ubuntu-M.ttf")
    if side=='front':
        centertext(fs,  font=ImageFont.truetype(ubuntum,90))
        centertext(fyn,  font=ImageFont.truetype(ubuntum,12))
        centertext(frontbtm,  font=ImageFont.truetype(ubuntum,12))
        centertext(frontfields,  font=ImageFont.truetype(ubuntum,12))
        centertext(lbltxt,  font=ImageFont.truetype(ubuntum,15))
    elif side=='back':
        centertext(backmgmt,  font=ImageFont.truetype(ubuntum,9),justify='center') 
        centertext(backfields,  font=ImageFont.truetype(ubuntum,9),justify='center') 
        centertext(backblurb,  font=ImageFont.truetype(ubuntum,9),justify='center') 
        
        
    else:
        return None
    
    
    return tag 


#objfn - what to sheetify, n - number of modules in (x-direction, y-direction), lw - linewidth, res - resolution
def sheetify(objfn,n=(2,6),lw=3,res=100,lbllist=None,side='front'):
    N=n[0]*n[1]
    if len(n)==2:
        nx,ny=n 
    else:
        return None
    
    if lbllist is None:
        lbllist=['' for x in range(N)]
    elif len(lbllist)<N:
        [lbllist.append('') for x in range(N-len(lbllist))]
    sheetsize=(round(res*8.5),round(res*11.0))#fits to 8.5"x11" sheet
    shtbox=(0,0,round(sheetsize[0]/nx),round(sheetsize[1]/ny))
    sheet=Image.new('RGB',sheetsize,color='white')#image basefile
    drsh=ImageDraw.Draw(sheet)#drawing
    for i in range(nx): 
        for j in range(ny):
            nn=i*n[1]+j#gets current index 1-dimensionally - if order of fors changes this needs to change too
            obj=objfn(res,n,lbl=lbllist[nn],side=side)
            sheet.paste(obj,[round(x) for x in [shtbox[0]+i*shtbox[2],shtbox[1]+j*shtbox[3],shtbox[0]+i*shtbox[2]+obj.size[0],shtbox[1]+j*shtbox[3]+obj.size[1]]])
            drsh.line( (0,j*sheetsize[1]/ny,sheetsize[0],j*sheetsize[1]/ny), fill=0,width=lw) #horizontals
        drsh.line( (i*sheetsize[0]/nx,0,i*sheetsize[0]/nx,sheetsize[1]), fill=0,width=lw) #vertical
    return sheet
def frontAndBack(objfn,n=(2,6),lw=3,res=100,lbllist=None):
    sheets=[]
    for s in ['front','back']:
        sheets.append(sheetify(objfn,n,lw,res,lbllist,side=s))
    return sheets
        
#
def alphabet(rng={'upper'}):
    alph=[]
    rngs={'lower':(97,122),'upper':(65,90)}#ranges of ascii locations - inclusive
    for r in rng:
        if r not in rngs.keys():
            pass
        else:
            for loc in range(*rngs[r]):
                alph.append(chr(loc))
    return list(alph)
#
def randomLabels(n=(2,6),numspots=2):
    alph=alphabet()
    ralph=[]
    for nn in range(n[0]*n[1]):
        spots=''
        for s in range(numspots):
            r=random.randint(0,len(alph)-1)
            spots=spots+alph[r]
        
        ralph.append(spots)
            
    return ralph
#base method, can just run w/o arguments for good output
    #
def renderSheets(n=(2,6),lw=3,res=100,lblmethod='random',numsheets=1):
    sheets=[]
    for sht in range(numsheets):
        if lblmethod=='random':
            lbllist=randomLabels(n=n)
        sheets.append(frontAndBack(objfn=soldTag,n=n,lw=lw,res=res,lbllist=lbllist))
    return sheets
    
###
"""
#@TODOs
    
"""
