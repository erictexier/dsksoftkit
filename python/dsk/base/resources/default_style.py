### some define style ####

styleUser = '''
QWidget {
    color:%(TEXTCOLOR)s;background:%(BGCOLOR)s;
    selection-color: %(SELECTCOLOR)s;
    selection-background-color: %(SELECTBGCOLOR)s;
    font-size: %(FONTSIZE)spt;
}
QLabel
{
    background-color: none;
    border:none;
}
QWebView {
    background:#ffffff;
}
QLineEdit {
      border: 1px solid gray;
     padding: 0 4px;
 }

QScrollBar:vertical{
    background: %(BGCOLOR)s;
}
QScrollBar:horizontal {
    background: %(BGCOLOR)s;
}
QScrollBar::add-page:vertical {
    background: none;
}
QScrollBar::sub-page:vertical {
    background: none;
}
QScrollBar::add-page:horizontal {
    background: none;
}
QScrollBar::sub-page:horizontal {
    background: none;
}

QHeaderView::section
{
background-color:%(BGCOLOR)s;
}
QTableCornerButton::section
{
    background-color:%(BGCOLOR)s;
}
QTabBar::tab
{
    background-color: transparent;
}

QTabBar::tab::selected
{
background-color: %(SELECTBGCOLOR)s;
}
'''
"""
try:
    import os
    pp = os.path.join(os.path.dirname(__file__),'css','std_dark.css')
    f = open(pp, "rt")
    shotgunStyle = f.read()
    # resolve tokens
    #qss_data = self._resolve_sg_stylesheet_tokens(qss_data)
    f.close()
except Exception as e:
    print(e)
"""