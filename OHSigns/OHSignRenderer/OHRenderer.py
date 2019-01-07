
class Module(object):#graphical object representing certain aspect of sign, can contain other modules - has css-like attributes & pseudo-elements
    def __init__(self):
        pass


def renderSign():
	pass

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
