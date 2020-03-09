import types 
# order in important
BASICTYPE = [float,
             int,
             int,
             bool,
             bytes,
             str
             ]

LISTTYPE = [list,
            tuple
            ]
DICTTYPE = [dict]

RAW_TYPE_VALUE = BASICTYPE + LISTTYPE + DICTTYPE
CashType = {}
for t in RAW_TYPE_VALUE:
    CashType[t.__name__] = t



SIMPLE_TYPE_NAME = [type.__name__ for type in BASICTYPE]
STRING_TYPE_NAME = [t.__name__ for t in (str,)]
LIST_TYPE_NAME =   [type.__name__ for type in LISTTYPE]


SOMEOTHERTYPE = ["set","xrange","complex"]


