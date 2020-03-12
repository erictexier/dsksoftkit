import traceback
from dsk.base.widgets.simpleqt import QtT,QtE
DO_PYQT4 = (QtT.which == 'PyQt4')

from dsk.base.utils.disk_utils import DiskUtils
from dsk.base.utils.msg_utils import MsgUtils as log

from dsk.base.resources import browser_signal as confsig
from dsk.base.resources import browser_constant as BK
from dsk.base.lib.msg_arg import MsgFirstTime


def get_unique_widget_name(dock_dict, name):
    """Return a uniquename

        :param dock_dict: list of existing name in a dictionary
        :param name: a proposed name use to build a root
        :return unique: a unique widget name

    """

    findname = name
    i = 1
    while findname in dock_dict:
        findname = name + '_' + str(i)
        i += 1
    return findname


def H_documentation(widgetApp, htmlFile):
    if htmlFile == None:
        log.error("no html file to display")
        return
    #if QtE.QtWebKit == None:
    #    from dsk.base.widgets.simpledoc_dialog_widget import SimpleDocDialogWidget
    #    dia = SimpleDocDialogWidget(widgetApp, htmlFile)
    #    dia.show()
    #    dia.exec_()
    #    return

    fr = QtT.QtWidgets.QDialog(widgetApp)
    layout = QtT.QtWidgets.QVBoxLayout()
    view = QtE.QWebView(fr)
    view.load(QtT.QtCore.QUrl(htmlFile))
    view.page().setViewportSize(view.page().mainFrame().contentsSize())
    #view.page().findText("SELECTION", QtWebKit.QWebPage.FindCaseSensitively)
    layout.addWidget(view)
    fr.setLayout(layout)
    view.show()
    fr.show()

ahtml = '''<html>
<head>
<h2> Quick Start </h2>
</head>
<body>
<h6>
%s
</h6>
</body>
</html>'''

def H_webpagequickstart(widgetApp, text):
    if text == None:
        return
    #if QtE.QtWebKit == None:
    #    from dsk.base.widgets.simpledoc_dialog_widget import SimpleDocDialogWidget
    #    dia = SimpleDocDialogWidget(widgetApp,text)
    #    dia.show()
    #    dia.exec_()
    #    return
    text = text.replace("\n","<br>")
    fr = QtE.QtWidgets.QDialog(widgetApp)
    layout = QtE.QtWidgets.QVBoxLayout()
    #page = QWebPage()
    view = QtE.QWebView(fr)
    view.setHtml(ahtml % text)
    view.page().setViewportSize(view.page().mainFrame().contentsSize())

    layout.addWidget(view)
    fr.setLayout(layout)
    view.show()
    fr.show()
################################################
## SUBMENU OPTION MANAGEMENT
##
def H_addSubOptionMenu(widgetApp,amenu,aname,dd):
    alreadyThere = [x for x in [x for x in amenu.actions() if str(x.text()) == aname]]
    if len(alreadyThere) == 0:
        if dd == None or len(dd) == 0:
            amenu.addAction(aname)
        else:

            subMenu = QtT.QtWidgets.QMenu(aname, amenu)
            subMenu.setObjectName(aname)
            amenu.addMenu(subMenu)

            for a in dd:

                if len(dd[a]) == 4:
                    la = dd[a][BK.K_TOOL_LABEL]
                    subMenu2 = QtT.QtWidgets.QMenu(la, widgetApp)
                    subMenu2.setObjectName(a)
                    subMenu.addMenu(subMenu2)
                    for b in dd[a][BK.K_TOOL_EXTRA]:
                        act = subMenu2.addAction(b)
                        act.setObjectName(b)
                elif len(dd[a]) == 3:
                    la = dd[a][BK.K_TOOL_LABEL]
                    act = subMenu.addAction(la)
                    act.setObjectName(a)
                    if dd[a][BK.K_TOOL_CHECKABLE]:
                        act.setCheckable(True)
                        act.setChecked(dd[a][BK.K_TOOL_DEFAULT])
                else:
                    log.error("in H_addSubOptionMenuwrong submenu description %s" % dd[a])



def printChildrenInfo(label,amenu):
    print("\nPRINT",amenu.objectName())
    for ch in amenu.children():
        if hasattr(ch,"text"):
            print(label,ch,"'",ch.text(),"'",ch.objectName())
        else:
            print("M",label,ch,ch.objectName())
    print("END PRINT",amenu.objectName())
    print("\n")

def H_removeSubOptionMenu(amenu,aname):
    alreadyThere = [(x,str(x.text())) for x in [x for x in amenu.actions() if str(x.text()) == aname]]
    if len(alreadyThere) == 1:
        #log.msg("removing the action %r-%r" % (alreadyThere[0][0],alreadyThere[0][1]))
        amenu.removeAction(alreadyThere[0][0])

    #####
    for sm in amenu.children():
        if sm.objectName() == aname:
            #log.info("clearing the menu %s" % aname)
            #printChildrenInfo("\tSubMenu",sm)
            for ssm in sm.children():
                if hasattr(ssm,'clear'):
                    ssm.clear()
                #printChildrenInfo("\t\tSubMenu",ssm)
                ssm.deleteLater()
            sm.clear()
            #printChildrenInfo("\tSubMenuEnd",sm)
            sm.deleteLater()
            break

def H_optionCallback(widgetApp,action):
    ## toDo: missing the value when check

    callerId = list()
    while(action.parent()!=None):
        callerId.insert(0,str(action.objectName()))
        if hasattr(action,"isCheckable") and action.isCheckable():
            callerId.insert(1,action.isChecked())
        action = action.parent()
    callerId = [x for x in callerId if x != ''] # remove empty

    if len(callerId) == 2:
        # we catch here the basic hide dock signal
        if callerId[0] in widgetApp._docksWidget:
            if callerId[1] == BK.ST_HIDE:
                widgetApp._docksWidget[callerId[0]].hide()
                return
            elif callerId[1] == BK.ST_SHOW:
                widgetApp._docksWidget[callerId[0]].show()
                return
            elif callerId[1] == BK.ST_VISIBLE:
                if widgetApp._docksWidget[callerId[0]].isVisible():
                    widgetApp._docksWidget[callerId[0]].hide()
                else:
                    widgetApp._docksWidget[callerId[0]].show()
                return
    widgetApp.sig[confsig.OPTION_CHANGE.name].emit(callerId)

################################################
## TOOL INSTANCIATION
##

def H_toolInstanciate(widgetApp,editor,widgetNameAction,aname=""):

    widgetName = ""
    isNew = False
    if not isinstance(widgetNameAction,str):
        widgetN = str(widgetNameAction.text())
        isNew = True
        for i in widgetApp._toolList:
            if widgetN == widgetApp._toolList[i].name:
                widgetName = i
                break
    else:
        widgetName = str(widgetNameAction)

    if not widgetName in list(widgetApp._toolList.keys()):
        return


    # reject if unique and already in there
    if widgetApp._toolList[widgetName].unique == True:
        if widgetApp._toolList[widgetName].name in widgetApp._docksWidget:
            log.warning("this widget can only be instantiate once")
            # let be sure that it's visible then
            widgetApp._docksWidget[widgetApp._toolList[widgetName].name].show()
            return


    widgetApp.setCursor(QtT.QtCore.Qt.WaitCursor)
    uniqueName = ""
    # find a unique name
    if aname == "":
        uniqueName = get_unique_widget_name(widgetApp._docksWidget,
                                     widgetApp._toolList[widgetName].name)
    else:
        #uniqueName = widgetApp.getWidgetName(aname)
        uniqueName = get_unique_widget_name(widgetApp._docksWidget,aname)


    wclass = widgetApp._toolList[widgetName].get_factory()
    wclassn = widgetApp._toolList[widgetName].wid_class
    if wclass == None:
        log.error("can't load %r" % (widgetName))
        traceback.print_exc()
        widgetApp.setCursor(QtT.QtCore.Qt.ArrowCursor)
        return

    cmd = "from dsk.base.widgets.app_dock_widget import DockWidget\n"
    cmd += widgetApp._toolList[widgetName].str_import()+"\n"
    cmd += "widgetApp._docksWidget[%r] = DockWidget(widgetApp,%r,%s,False)" % (
                                                uniqueName, uniqueName,wclassn)

    try:
        exec(cmd)
    except:
        log.error("can't create %r in dock" % (widgetName))
        traceback.print_exc()
        widgetApp.setCursor(QtT.QtCore.Qt.ArrowCursor)
        return
    log.info("Creating dockTools %r(%r)" % (uniqueName, widgetName))

    widgetApp._docksWidget[uniqueName].setObjectName("D"+uniqueName)

    widgetApp._docksWidget[uniqueName].setFeatures(QtT.QtWidgets.QDockWidget.DockWidgetMovable |
                                                   QtT.QtWidgets.QDockWidget.DockWidgetFloatable |
                                                   QtT.QtWidgets.QDockWidget.DockWidgetClosable)

    prefArea = QtT.QtCore.Qt.RightDockWidgetArea

    if isNew == True:
        upref = widgetApp._toolList[widgetName].pref_place
        if upref == "L":
            prefArea = QtT.QtCore.Qt.LeftDockWidgetArea
        elif upref == 'T':
            prefArea = QtT.QtCore.Qt.TopDockWidgetArea
        elif upref == "B":
            prefArea = QtT.QtCore.Qt.BottomDockWidgetArea

    widgetApp.addDockWidget(prefArea,widgetApp._docksWidget[uniqueName])
    # time for each widget to register there signal
    widgetApp._docksWidget[uniqueName].registerWidget(editor)

    msg = MsgFirstTime(widgetApp._docksWidget[uniqueName].getCustomWidget())
    widgetApp.sig[confsig.INIT_FIRST_TIME.name].emit(msg)
    # submenu registration

    om = widgetApp._toolList[widgetName].optmenu
    if om != None:
        widgetApp.addSubOptionMenu(uniqueName,om)

    widgetApp.setCursor(QtT.QtCore.Qt.ArrowCursor)

################################################
## LAYOUT MANAGEMENT
def H_updateLayout(widgetApp, editor):
    widgetApp._layoutMenu.clear()
    savedLayout = editor.get_layout_names()
    for layout in savedLayout:
        widgetApp._layoutMenu.addAction(widgetApp.tr(layout))

    widgetApp._layoutMenu.addSeparator()
    widgetApp._layoutMenu.addAction("Save current layout: %s" % editor.get_layout_file())
    widgetApp._layoutMenu.addAction("Save as...")
    widgetApp._layoutMenu.addAction("Clear")

#######################
def H_layoutAction(widgetApp,editor,action):
    actionName = str(action.text())
    if actionName.startswith("Save current layout"):
        if editor.get_layout_file() == "":
            editor.set_layout_file("defaultLayout")
            widgetApp.updateLayout()
        widgetApp.saveLayout(editor.get_layout_file())

    elif actionName.startswith("Save as..."):
        text, ok = QtT.QtWidgets.QInputDialog.getText(widgetApp,
                                              widgetApp.tr("Save New Layout"),
                                              widgetApp.tr("Layout Name"),
                                              QtT.QtWidgets.QLineEdit.Normal,'MyLayout')
        if ok and not text.isEmpty():
            lf = str(text)
            editor.set_layout_file(lf)
            widgetApp.saveLayout(lf)
            widgetApp.updateLayout()
    elif actionName == "Clear":
        widgetApp.clearAllDocks()
        QtT.QtWidgets.QApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        QtT.QtWidgets.QApplication.processEvents()

    else:
        widgetApp.clearAllDocks()
        QtT.QtWidgets.QApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
        QtT.QtWidgets.QApplication.processEvents()
        editor.set_layout_file(actionName)
        widgetApp.loadLayout(actionName)
        widgetApp.updateLayout()

#######################
def H_saveLayout(widgetApp,editor,nameLayout):
    afile = editor.layout_file(nameLayout)

    widgets = []
    for w in widgetApp._docksWidget:
        widgets.append(QtT.QtCore.QString(w))

    settings = QtT.QtCore.QSettings(afile, QtT.QtCore.QSettings.IniFormat, None)
    settings.clear()
    if DO_PYQT4:
        settings.setValue('MainWindow/name', QtT.QtCore.QVariant(nameLayout))
        settings.setValue('MainWindow/state', QtT.QtCore.QVariant(widgetApp.saveState()))
        settings.setValue('MainWindow/size', QtT.QtCore.QVariant(widgetApp.size()))
        settings.setValue('MainWindow/pos', QtT.QtCore.QVariant(widgetApp.pos()))
        settings.setValue('MainWindow/widgets', QtT.QtCore.QVariant(widgets))
    else:
        settings.setValue('MainWindow/name', nameLayout)
        settings.setValue('MainWindow/state', widgetApp.saveState())
        settings.setValue('MainWindow/size', widgetApp.size())
        settings.setValue('MainWindow/pos', widgetApp.pos())
        settings.setValue('MainWindow/widgets', widgets)

    for w in widgetApp._docksWidget:
        ww = widgetApp._docksWidget[w].getCustomWidget()
        className = ww.__class__.__name__
        if DO_PYQT4:
            settings.setValue('%s/classname' % w, QtT.QtCore.QVariant(className))
            settings.setValue('%s/size' % w, QtT.QtCore.QVariant(ww.size()))
            settings.setValue('%s/pos' % w, QtT.QtCore.QVariant(ww.pos()))
            settings.setValue('%s/floating' % w, QtT.QtCore.QVariant(widgetApp._docksWidget[w].isFloating()))
        else:
            settings.setValue('%s/classname' % w, className)
            settings.setValue('%s/size' % w, ww.size())
            settings.setValue('%s/pos' % w, ww.pos())
            settings.setValue('%s/floating' % w, widgetApp._docksWidget[w].isFloating())


#######################
def H_loadLayout(widgetApp,editor,aDefautPathMgr,nameLayout):

    if nameLayout == "":
        log.info("not layout file specified")
        widgetApp.resize(500,500)
        widgetApp.move(100,100)
        return
    afile = editor.layout_file(nameLayout)

    if not DiskUtils.is_file_exist(afile):
        afile = aDefautPathMgr.getDefaultLayoutFile()
        if not DiskUtils.is_file_exist(afile):
            log.debug("cannot find the layout file %s" % afile)
            widgetApp.resize(500,500)
            widgetApp.move(100,100)
            return

    settings = QtT.QtCore.QSettings(afile, QtT.QtCore.QSettings.IniFormat, None)
    if DO_PYQT4:
        widgetApp.resize(settings.value('MainWindow/size').toSize())
        widgetApp.move(settings.value('MainWindow/pos').toPoint())
        widgets = list(map(str, settings.value('MainWindow/widgets').toStringList()))
        for w in widgets:
            className = str(settings.value('%s/className' % w).toString())
            widgetApp.toolInstanciate(className,w)
        widgetApp.restoreState(settings.value('MainWindow/state').toByteArray())
        for w in widgets:
            if w  in widgetApp._docksWidget:
                widgetApp._docksWidget[w].getCustomWidget().resize(settings.value('%s/size' % w).toSize())
                isFloating = settings.value('%s/floating' % w).toBool()
                if isFloating:
                    widgetApp._docksWidget[w].getCustomWidget().move(settings.value('%s/pos' % w).toPoint())
    else:
        widgetApp.resize(settings.value('MainWindow/size'))
        widgetApp.move(settings.value('MainWindow/pos'))
        widgets = settings.value('MainWindow/widgets')
        if widgets != None:
            for w in widgets:
                className = str(settings.value('%s/className' % w))
                widgetApp.toolInstanciate(className,w)
            widgetApp.restoreState(settings.value('MainWindow/state'))
            for w in widgets:
                if w  in widgetApp._docksWidget:
                    widgetApp._docksWidget[w].getCustomWidget().resize(settings.value('%s/size' % w))
                    isFloating = settings.value('%s/floating' % w)
                    if isFloating:
                        widgetApp._docksWidget[w].getCustomWidget().move(settings.value('%s/pos' % w))


def H_removeDock(widgetApp, editor,name):
    ''' call from the dock widget '''
    assert name in widgetApp._docksWidget
    widgetApp.removeSubOptionMenu(name)
    w = widgetApp._docksWidget.pop(name)
    w.deregisterWidget(editor)
    widgetApp.removeDockWidget(w)
    w.deleteLater()

###
def H_clearAllDocks(widgetApp):
    allDock = list(widgetApp._docksWidget.values())[:]
    for d in allDock:
        d.close()
    widgetApp.clearMenuOption()
    widgetApp._docksWidget.clear()

###
# menu
def H_prefMenu(widgetApp):
    ##############
    # preference menu
    #############
    prefMenu = QtT.QtWidgets.QMenu(widgetApp.tr("&Preferences"), widgetApp)
    prefMenu.addAction(widgetApp.tr("change color text"))
    prefMenu.addAction(widgetApp.tr("change color bg"))
    prefMenu.addAction(widgetApp.tr("change color select"))
    prefMenu.addAction(widgetApp.tr("change color bgselect"))
    prefMenu.addSeparator()
    # rich color
    prefMenuRich = QtT.QtWidgets.QMenu(widgetApp.tr("Info Color"),prefMenu)
    #prefMenuRich = QtWidgets.QMenu(widgetApp.tr("Info Color"))
    prefMenuRich.addAction(widgetApp.tr("Label Color"))
    prefMenuRich.addAction(widgetApp.tr("Value Color"))
    prefMenuRich.addAction(widgetApp.tr("Valid Color"))
    prefMenuRich.addAction(widgetApp.tr("Hilite Color"))
    prefMenuRich.addAction(widgetApp.tr("Error Color"))
    prefMenu.addMenu(prefMenuRich)
    prefMenu.addSeparator()
    #widgetApp.connect(prefMenuRich,QtCore.SIGNAL("triggered(QAction *)"), widgetApp.prefAction)


    # font
    fontMenu = QtT.QtWidgets.QMenu(widgetApp.tr("Font Size"),prefMenu)
    for fs in range(8,20,2):
        fontMenu.addAction(widgetApp.tr("%d" % fs))
    prefMenu.addMenu(fontMenu)
    prefMenu.addSeparator()
    prefMenu.addAction(widgetApp.tr("Reset Default"))
    prefMenu.addSeparator()
    return prefMenu

######################
def H_prefAction(widgetApp,editor,action):

    actstring = str(action.text())

    if actstring.startswith("Reset"):
        editor.reset_style_preference(widgetApp)

    elif actstring.endswith("text"):
        color = QtT.QtWidgets.QColorDialog.getColor(QtT.QtGui.QColor(editor.get_text_color()), widgetApp)
        if color.isValid():
            editor.set_text_color(color, widgetApp)

    elif actstring.endswith("bg"):
        color = QtT.QtWidgets.QColorDialog.getColor(QtT.QtGui.QColor(editor.get_bg_color()), widgetApp)
        if color.isValid():
            editor.set_bg_color(color, widgetApp)

    elif actstring.endswith("bgselect"):
        color = QtT.QtWidgets.QColorDialog.getColor(QtT.QtGui.QColor(editor.get_select_bg_color()), widgetApp)
        if color.isValid():
            editor.set_select_bg_color(color, widgetApp)

    elif actstring.endswith("select"):
        color = QtT.QtWidgets.QColorDialog.getColor(QtT.QtGui.QColor(editor.get_select_color()), widgetApp)
        if color.isValid():
            editor.set_select_color(color, widgetApp)

    elif actstring.endswith("Color"):
        aw = actstring.split()[0]
        d = editor.get_rich_color()
        assert aw in d
        color = QtT.QtWidgets.QColorDialog.getColor(QtT.QtGui.QColor(d[aw]), widgetApp)
        if color.isValid():
            d[aw] = str(color.name())
            widgetApp.sig[confsig.RICH_COLOR_CHANGE.name].emit(d)

    elif actstring == "startLog":
        editor.start_log()
    elif actstring == "endLog":
        editor.end_log()
    else:
        try:
            fontSize = int(actstring)
            editor.set_font_size(fontSize, widgetApp)
        except:
            pass
