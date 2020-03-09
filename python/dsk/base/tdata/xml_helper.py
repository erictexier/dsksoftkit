import os
import base64
import types

import xml.dom as Dom
from xml.dom.minidom import parse, parseString

from dsk.base.utils.msg_utils import MsgUtils
from dsk.base.utils.disk_utils import DiskUtils

class XmlHelper(object):
    """ some top class xml utils
    """
    __encoding = 'UTF-8'

    ##################
    def __init__(self,enc):
        super(XmlHelper,self).__init__()
        self._doc = None
        self._ENCODECDATA = enc
        self._callBack = {}

    ##################
    def getEncoding(self):
        return XmlHelper.__encoding
    ##################
    def setEncoding(self,enc):
        XmlHelper.__encoding = enc
    ##################

    def reset(self):
        # to avoid memory leak
        if self._doc != None:
            self._doc.unlink()
        self._doc = None

    ##################
    def createDom(self,nsUri,qualifName,dtName):
        self.reset()
        # for now, we live the doctype 'dtd' out.
        dt = None #Dom.getDOMImplementation().createDocumentType("","","")

        self._doc = Dom.getDOMImplementation().createDocument(nsUri,qualifName,dt)

    ##################
    def getDoc(self):
        return self._doc

    #################
    def isGz(self,filename):
        return os.path.splitext(filename)[1] ==  ".gz"

    ##################
    def OpenFileGz(self, afile,mode = "r"):
        import gzip
        fFile = None
        if mode == "r":
            try:
                fFile = gzip.open( afile, "rb")
            except IOError:
                    # can't read the file
                    MsgUtils.error("Can't read %s" % afile)
                    fFile = None
        else:
            try:
                fFile = gzip.open(afile, "wb")
            except IOError:
                MsgUtils.error("Can't read %s" % afile)
                fFile = None
        return fFile

    ##################
    def OpenFile(self, afile , mode = "r"):
        try:
            fFile = open(afile, mode)
        except:
            MsgUtils.error("Can't open %s" % afile)
            fFile = None

        return fFile

    ##################
    def serialize(self,elmt=None):
        """ return a str of elm
        """
        if elmt == None: # serialize the entier doc
            if self._doc == 0:
                return ""
            elmt = self._doc
        return elmt.toxml()

    ##################
    def deserialize(self, astr):
        if self._doc != None:
            MsgUtils.warning("Be Carrefull the older document will be erase")
        self.reset()
        self._doc  = parseString(astr)

    ##################
    def importFromFile(self, fileName):
        if self.isGz(fileName) == True:
            f = self.OpenFileGz(fileName,"r")
            if f != 0:
                astr = f.read()
                self.reset()
                self._doc = parseString(astr)
                f.close()
                return True
        else:
            self.reset()
            if DiskUtils.is_file_exist(fileName):
                try:
                    self._doc = parse(fileName)
                except:
                    MsgUtils.error('Trouble in parsing %s' % fileName)
                    return False
            else:
                return False
            return True

        return False

    ##################
    def exportToFile(self,fileName,pretty = False):
        f = None
        if self.isGz(fileName) == True:
            f = self.OpenFileGz(fileName,"w")
        else:
            f = self.OpenFile(fileName,"w")
        #print("OPEN %s" % fileName)
        if f != 0 and f != None:
            self.write(f,pretty)
            f.close()
            return True
        return False

    ##################
    def write(self, afile="",pretty=False):
        if afile != "":
            if self._doc == None:
                MsgUtils.warning("has no document")
                return False
            try:
                #if pretty:
                #    print(self.getEncoding())
                #    pstr = self._doc.toprettyxml("\t", "\n", self.getEncoding())
                #    afile.write(pstr)

                #else:
                self._doc.writexml(afile,
                            "\t",
                            "\t",
                            "\n",self.getEncoding())

            except Exception as e:
                MsgUtils.error(str(e))
                MsgUtils.error("can't write the current document")
                return False
            return True
        else:
            if self._doc != None:
                if pretty:
                    print(str(self._doc.toprettyxml("\t","\n",self.getEncoding())))
                else:
                    print(self._doc.toxml(self.getEncoding()))
                return True
        return False

    #################
    def addCallBack(self,key,funct):
        self._callBack[key] = funct

    #################
    def doCallBack(self,key,values):
        if key in self._callBack:
            return self._callBack[key](key,values)
        return None

    #################
    def getElementsByTagName(self,tagName):
        return self._doc.getElementsByTagName(tagName)[0]

    #################
    def getXmlAttr(self,elmt,adict):
        a = elmt.attributes
        if a == None:
            return False
        found =  False
        for index in range(a.length):
            item = a.item(index)
            adict[item.name] = item.value
            found =  True
        return found

    ##################
    def elementUnder(self, parent, name, attributes=()):
        """creates element inside of parent and returns it,
        attributes are as sequence of (name,value) sequences"""
        a = self._doc.createElement( name)
        parent.appendChild( a)
        if attributes:
            for i in attributes:
                a.setAttribute( i[0], str(i[1]))
        return a

    ##################
    def textNodeUnder(self,parent,aString):
        assert type(aString) == str

        if aString.strip() == aString and aString != "":
            if self._ENCODECDATA == True:
                valval = self._doc.createTextNode(base64.encodestring(aString))
            else:
                valval = self._doc.createTextNode(aString)
            if parent != None:
                parent.appendChild(valval)
            return valval
        else:
            return self.cdataUnder(parent,aString)

    #################
    def getTextValue(self,n):
        assert n != None
        code = ""
        if self._ENCODECDATA == True:
            code = base64.decodestring(n.nodeValue)
        else:
            code = n.nodeValue
        return code

    ##################
    def cdataUnder(self,parent,cmd):
        cds = self._doc.createCDATASection(base64.encodestring(cmd))
        parent.appendChild(cds)
        return cds

    ##################
    def getcData(self,n):
        assert n != None
        code = base64.decodestring(n.nodeValue)
        return code
