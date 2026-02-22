#------------------------------------------------------------------------------
# File:
#   gui.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file executes manages the GUI for the "Simple Double Entry Tool".
#
#------------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from entry import Line
from entry import Entry


# Generic Fonts
FONT_FRAME    = ('Calibri', 8, 'italic underline')
FONT_LABEL    = ('Calibri', 10, 'bold')
FONT_BOXES    = ('Calibri', 10)
FONT_CHOICES  = ('Calibri', 8)
FONT_SELECTED = ('Calibri', 8, 'bold')

WSCALE = 4


class MyGui():
    ''' Class to hold all GUI functionality '''

    # Constrain sizes to make GUI deisgn more simple
    NUM_COLS = 39
    NUM_ROWS = 41
    COL_SIZE = 30
    ROW_SIZE = 20

    selectedAcct = ''
    simpleEntry = True
    stopScroll = False

    # -------------------------------------------------------------------------
    def __init__(self):
        self.root = tk.Tk()
        self._BuildGui()
        self._BindEvents()

    # -------------------------------------------------------------------------
    def _BuildGui(self):
        root = self.root

        # Application Title
        root.title('EmbeddedForest')

        # Define root grid
        for i in range(self.NUM_COLS):
            root.columnconfigure(i, minsize=self.COL_SIZE, weight=2)
        for i in range(self.NUM_ROWS):
            root.rowconfigure(i, minsize=self.ROW_SIZE, weight=2)

        self._BuildTitleFrame()
        self._BuildSetupFrame()
        self._BuildDataFrame()
        self._BuildPreviewFrame()

        #----------------------------------------------------------------------
        # Create Notebook
        #----------------------------------------------------------------------
        self.nbRs = 13
        self.nbCs = 37

        self.notebook = ttk.Notebook(
            self.root
        )
        self.notebook.grid(
            row        =14,
            column     =1,
            rowspan    =self.nbRs,
            columnspan =self.nbCs,
            sticky     ='nesw'
        )

        self._BuildSimpleEntryTab()
        self._BuildSplitEntryTab()
        self._BuildScrollableFrame()

        #----------------------------------------------------------------------
        # Root Buttons
        #----------------------------------------------------------------------
        # Add Entry Button
        self.addEntryButton = tk.Button(
            root,
            text        ='Add Entry',
            font        =FONT_LABEL
        )
        self.addEntryButton.grid(
            row         =28,
            column      =12,
            sticky      ='nesw',
            padx        =10,
            pady        =0,
            rowspan     =2,
            columnspan  =6
        )

        # Redo Entry Button
        self.redoButton = tk.Button(
            root,
            text        ='Redo Entry',
            font        =FONT_LABEL
        )
        self.redoButton.grid(
            row         =28,
            column      =21,
            sticky      ='nesw',
            padx        =10,
            pady        =0,
            rowspan     =2,
            columnspan  =6
        )

    # -------------------------------------------------------------------------
    # Title Frame
    # -------------------------------------------------------------------------
    def _BuildTitleFrame(self):
        # Frame
        f = self._FrameHelper(self.root, 1, 2, 5, 13)

        # Title 1
        tmp = tk.Label(
            f,
            text       ='S-DET',
            font       =('Calibri', 32, 'bold italic')
        )
        tmp.grid(
            row        =0,
            column     =4,
            rowspan    =3,
            columnspan =9,
            sticky     ='nesw'
        )

        # Title 2
        tmp = tk.Label(
            f,
            text       ='A Simple Double Entry Tool',
            font       =('Calibri', 12, 'italic')
        )
        tmp.grid(
            row        =3,
            column     =4,
            rowspan    =2,
            columnspan =9,
            sticky     ='nesw'
        )

        # Logo
        logo = ImageTk.PhotoImage(Image.open('tree.png'))
        tmp = tk.Label(f, image=logo)
        tmp.image = logo    # Necessary bc of python garabge collection
        tmp.grid(row=0, column=0, sticky='nesw', rowspan=5, columnspan=4)

    # -------------------------------------------------------------------------
    # Setup Frame
    # -------------------------------------------------------------------------
    def _BuildSetupFrame(self):
        # Frame
        f = self._FrameHelper(self.root, 1, 17, 5, 21)

        # Setup Label
        tmp = tk.Label(
            f,
            text        ='Setup',
            font        =FONT_FRAME
        )
        tmp.grid(
            row         =0,
            column      =0,
            rowspan     =1,
            columnspan  =5,
            sticky      ='w'
        )

        # Import File Label
        tmp = tk.Label(
            f,
            text        ='Import File:',
            font        =FONT_LABEL
        )
        tmp.grid(
            row         =1,
            column      =0,
            rowspan     =1,
            columnspan  =5,
            sticky      ='e'
        )

        # Associated Account Label
        tmp = tk.Label(
            f,
            text        ='Associated Account:',
            font        =FONT_LABEL
        )
        tmp.grid(
            row         =3,
            column      =0,
            rowspan     =1,
            columnspan  =5,
            sticky      ='e'
        )

        # Import Dropdown
        self.selectedImportFile = tk.StringVar()
        self.importDropdown = ttk.Combobox(
            f,
            textvariable    =self.selectedImportFile,
            font            =FONT_BOXES,
            width           =int(11*WSCALE),
            state           ='readonly'
        )
        self.importDropdown.grid(
            row             =1,
            column          =5,
            rowspan         =1,
            columnspan      =11,
            sticky          ='w'
        )

        # Associated Account Dropdown
        self.selectedAssAcct = tk.StringVar()
        self.assAcctDropdown = ttk.Combobox(
            f,
            textvariable    =self.selectedAssAcct,
            font            =FONT_BOXES,
            width           =int(11*WSCALE),
            state           ='readonly'
        )
        self.assAcctDropdown.grid(
            row             =3,
            column          =5,
            rowspan         =1,
            columnspan      =11,
            sticky          ='w',
        )

        # Start Button
        self.startButton = tk.Button(
            f,
            text        ='Start',
            font        =FONT_LABEL
        )
        self.startButton.grid(
            row         =1,
            column      =16,
            rowspan     =3,
            columnspan  =5,
            padx        =20,
            pady        =10,
            sticky      ='nesw'
        )

    # -------------------------------------------------------------------------
    # Data Frame
    # -------------------------------------------------------------------------
    def _BuildDataFrame(self):
        # Frame
        f = self._FrameHelper(self.root, 8, 7, 4, 25)

        # Transaction Data Label
        tmp = tk.Label(
            f,
            text       ='Transaction Data',
            font       =FONT_FRAME
        )
        tmp.grid(
            row        =0,
            column     =0,
            rowspan    =1,
            columnspan =5,
            sticky     ='w'
        )

        # Date Label
        tmp = tk.Label(
            f,
            text       ='Date:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =1,
            column     =1,
            rowspan    =1,
            columnspan =3,
            sticky     ='w'
        )

        # Description Label
        tmp = tk.Label(
            f,
            text       ='Description:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =1,
            column     =5,
            rowspan    =1,
            columnspan =6,
            sticky     ='w'
        )

        # Amount Label
        tmp = tk.Label(
            f,
            text       ='Amount:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =1,
            column     =21,
            rowspan    =1,
            columnspan =4,
            sticky     ='w'
        )

        # Date Box
        self.displayDate = tk.StringVar(value='')
        tmp = tk.Entry(
            f,
            textvariable    =self.displayDate,
            font            =FONT_BOXES,
            width           =12,
            justify         ='center',
            state           ='readonly'
        )
        tmp.grid(
            row             =2,
            column          =1,
            sticky          ='w',
            rowspan         =1,
            columnspan      =3
        )

        # Description Box
        self.displayDescription = tk.StringVar(value=' ')
        tmp = tk.Entry(
            f,
            textvariable    =self.displayDescription,
            font            =FONT_BOXES,
            width           =64,
            justify         ='left',
            state           ='readonly'
        )
        tmp.grid(
            row             =2,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =15
        )

        # Amount Box
        self.displayAmount = tk.StringVar(value=' ')
        tmp = tk.Entry(
            f,
            textvariable    =self.displayAmount,
            font            =FONT_BOXES,
            width           =12,
            justify         ='center',
            state           ='readonly'
        )
        tmp.grid(
            row             =2,
            column          =21,
            sticky          ='w',
            rowspan         =1,
            columnspan      =3
        )

    # -------------------------------------------------------------------------
    # Preview Frame
    # -------------------------------------------------------------------------
    def _BuildPreviewFrame(self):
        # Frame
        f = self._FrameHelper(self.root, 31, 1, 9, 37)

        # Preview Label
        tmp = tk.Label(
            f,
            text       ='Preview',
            font       =FONT_FRAME
        )
        tmp.grid(
            row        =0,
            column     =0,
            rowspan    =1,
            columnspan =5,
            sticky     ='w'
        )

        # Preview box
        self.previewBox = tk.Text(
            f,
            font        =FONT_BOXES,
            width       =15,
            height      =8
        )
        self.previewBox.grid(
            row         =1,
            column      =1,
            sticky      ='nsew',
            rowspan     =7,
            columnspan  =35
        )

        # Scroll bar for preview box
        logScroll = tk.Scrollbar(
            f,
            orient      ='vertical',
            command     =self.previewBox.yview
        )
        self.previewBox.configure(yscrollcommand=logScroll.set)

        # Tags for different text types for log box
        self.previewBox.tag_configure(
            'header',
            background  ='white',
            foreground  ='black',
            font        =('consolas', 7, 'bold')
        )
        self.previewBox.tag_configure(
            'default',
            background  ='white',
            foreground  ='black',
            font        =('consolas', 7)
        )
        self.previewBox.tag_configure(
            'error',
            background  ='white',
            foreground  ='red',
            font        =('consolas', 7)
        )

    # -------------------------------------------------------------------------
    # Simple Entry Tab
    # -------------------------------------------------------------------------
    def _BuildSimpleEntryTab(self):
        simpleTab = tk.Frame(self.notebook)
        self.notebook.add(simpleTab, text='Simple Entry')

        # Define grid
        for i in range(self.nbRs):
            simpleTab.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)
        for i in range(self.nbCs):
            simpleTab.columnconfigure(i, minsize=self.COL_SIZE, weight=0)

        #----------------------------------------------------------------------
        # Assets
        #----------------------------------------------------------------------
        # Assets Label
        tmp = tk.Label(
            simpleTab,
            text       ='Assets:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =1,
            rowspan    =1,
            columnspan =8,
            sticky     ='nesw'
        )

        # Asset Category box
        self.assCatBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.assCatBox.grid(
            row         =1,
            column      =1,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.assCatBox.yview
        )
        self.assCatBox.configure(yscrollcommand=logScroll.set)
        self.assCatBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        # Asset Selection box
        self.assSelBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.assSelBox.grid(
            row         =1,
            column      =5,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.assSelBox.yview
        )
        self.assSelBox.configure(yscrollcommand=logScroll.set)
        self.assSelBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        #----------------------------------------------------------------------
        # Liabilities
        #----------------------------------------------------------------------
        # Liabilities Label
        tmp = tk.Label(
            simpleTab,
            text       ='Liabilities:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =10,
            rowspan    =1,
            columnspan =8,
            sticky     ='nesw'
        )

        # Liabilities Category box
        self.liaCatBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.liaCatBox.grid(
            row         =1,
            column      =10,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.liaCatBox.yview
        )
        self.liaCatBox.configure(yscrollcommand=logScroll.set)
        self.liaCatBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        # Liabilities Selection box
        self.liaSelBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.liaSelBox.grid(
            row         =1,
            column      =14,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.liaSelBox.yview
        )
        self.liaSelBox.configure(yscrollcommand=logScroll.set)
        self.liaSelBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        #----------------------------------------------------------------------
        # Income
        #----------------------------------------------------------------------
        # Income Label
        tmp = tk.Label(
            simpleTab,
            text       ='Income:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =19,
            rowspan    =1,
            columnspan =8,
            sticky     ='nesw'
        )

        # Income Category box
        self.incCatBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.incCatBox.grid(
            row         =1,
            column      =19,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.incCatBox.yview
        )
        self.incCatBox.configure(yscrollcommand=logScroll.set)
        self.incCatBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )
        # Income Selection box
        self.incSelBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.incSelBox.grid(
            row         =1,
            column      =23,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.incSelBox.yview
        )
        self.incSelBox.configure(yscrollcommand=logScroll.set)
        self.incSelBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        #----------------------------------------------------------------------
        # Expenses
        #----------------------------------------------------------------------
        # Expenses Label
        tmp = tk.Label(
            simpleTab,
            text       ='Expenses:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =28,
            rowspan    =1,
            columnspan =8,
            sticky     ='nesw'
        )

        # Expenses Category box
        self.expCatBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.expCatBox.grid(
            row         =1,
            column      =28,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.expCatBox.yview
        )
        self.expCatBox.configure(yscrollcommand=logScroll.set)
        self.expCatBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        # Expenses Selection box
        self.expSelBox = tk.Text(
            simpleTab,
            font        =FONT_CHOICES,
            width       =12,
            height      =8
        )
        self.expSelBox.grid(
            row         =1,
            column      =32,
            rowspan     =9,
            columnspan  =4,
            sticky      ='nsew'
        )
        logScroll = tk.Scrollbar(
            simpleTab,
            orient      ='vertical',
            command     =self.expSelBox.yview
        )
        self.expSelBox.configure(yscrollcommand=logScroll.set)
        self.expSelBox.tag_configure(
            'selected',
            background  ='light gray',
            foreground  ='black',
            font        =FONT_CHOICES
        )

        #----------------------------------------------------------------------
        # Memo
        #----------------------------------------------------------------------
        # Memo Label
        tmp = tk.Label(
            simpleTab,
            text       ='Memo:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =11,
            column     =11,
            rowspan    =1,
            columnspan =3,
            sticky     ='nesw'
        )

        # Memo Box
        self.memo = tk.StringVar(value='')
        tmp = tk.Entry(
            simpleTab,
            textvariable    =self.memo,
            font            =FONT_BOXES,
            width           =45,
            justify         ='left'
        )
        tmp.grid(
            row             =11,
            column          =14,
            sticky          ='w',
            rowspan         =1,
            columnspan      =12
        )

    # -------------------------------------------------------------------------
    # Split Entry Tab
    # -------------------------------------------------------------------------
    def _BuildSplitEntryTab(self):
        splitTab = ttk.Frame(self.notebook)
        self.notebook.add(splitTab, text='Split Entry')

        # Define grid
        for i in range(self.nbRs):
            splitTab.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)
        for i in range(self.nbCs):
            splitTab.columnconfigure(i, minsize=self.COL_SIZE, weight=0)

        # Line Label
        tmp = tk.Label(
            splitTab,
            text       ='Line:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =1,
            rowspan    =1,
            columnspan =2,
            sticky     ='w'
        )

        # Account Label
        tmp = tk.Label(
            splitTab,
            text       ='Account:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =3,
            rowspan    =1,
            columnspan =3,
            sticky     ='w'
        )

        # Memo Label
        tmp = tk.Label(
            splitTab,
            text       ='Memo:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =15,
            rowspan    =1,
            columnspan =3,
            sticky     ='w'
        )

        # Amount Label
        tmp = tk.Label(
            splitTab,
            text       ='Amount:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =0,
            column     =27,
            rowspan    =1,
            columnspan =3,
            sticky     ='w'
        )

        # Add Line Button
        self.addLineButton = tk.Button(
            splitTab,
            text        ='Add Line',
            font        =FONT_LABEL
        )
        self.addLineButton.grid(
            row         =2,
            column      =33,
            rowspan     =3,
            columnspan  =3,
            padx        =0,
            pady        =0,
            sticky      ='nesw',
        )

        # Remove Last Line Button
        self.removeLineButton = tk.Button(
            splitTab,
            text        ='Remove Last Line',
            font        =FONT_LABEL
        )
        self.removeLineButton.grid(
            row         =6,
            column      =33,
            rowspan     =3,
            columnspan  =3,
            padx        =0,
            pady        =0,
            sticky      ='nesw',
        )

        # Balance Label
        tmp = tk.Label(
            splitTab,
            text       ='Balance:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =10,
            column     =33,
            rowspan    =1,
            columnspan =3,
            sticky     ='nesw'
        )

        # Balance Box
        self.balanceStr = tk.StringVar(value='')
        amntBox = tk.Entry(
            splitTab,
            textvariable    =self.balanceStr,
            font            =FONT_BOXES,
            width           =4*WSCALE,
            justify         ='center',
            state           ='readonly'
        )
        amntBox.grid(
            row             =11,
            column          =33,
            sticky          ='nesw',
            rowspan         =1,
            columnspan      =3
        )

        self.splitTab = splitTab

        # Bind events
        self.addLineButton.configure(command=self._AddSplitRow)
        self.removeLineButton.configure(command=self._DeleteSplitRow)

    # -------------------------------------------------------------------------
    # Scrollable frame
    # -------------------------------------------------------------------------
    def _BuildScrollableFrame(self):
        # Create border around scrollable area
        self._FrameHelper(self.splitTab, 1, 1, self.nbRs-2, self.nbCs-6)

        # Canvas dims
        rs = 9
        cs = 29

        # Build and place canvas inside of split frame
        self.canvas = tk.Canvas(
            self.splitTab,
            height =rs*WSCALE,
            width =cs*WSCALE,
            borderwidth=0,
            highlightthickness=0
            # highlightcolor='gray',
        )
        self.canvas.grid(
            row        =2,
            column     =2,
            rowspan    =rs,
            columnspan =cs,
            padx        =0,
            pady        =0,
            sticky     ='nesw'
        )

        # Build grid for canvas
        for i in range(rs):
            self.canvas.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)
        for i in range(cs):
            self.canvas.columnconfigure(i, minsize=self.COL_SIZE, weight=0)

        # Add in scroll feature
        self.scrollbar = ttk.Scrollbar(
            self.canvas,
            orient="vertical",
            command=self.canvas.yview
        )

        # Create a frame inside the canvas which will be scrollable
        self.scrollFrame = tk.Frame(self.canvas)

        # Create grid for scrollable frame
        for i in range(rs):
            self.scrollFrame.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)
        for i in range(cs):
            self.scrollFrame.columnconfigure(i, minsize=self.COL_SIZE, weight=0)

        # Place scroll frame in window
        self.scrollFrameId = self.canvas.create_window(
            0, 0, window=self.scrollFrame, anchor='nw')

        # Bind events
        self.scrollFrame.bind('<Configure>', self._HandleConfigureEvent, add='+')
        self.canvas.bind_all("<MouseWheel>", self._HandleMouseWheelEvent, add='+')

        # Memo List
        self.rows = []

        # Create first three rows in split tab
        for _ in range(3):
            self._AddSplitRow()

    # -------------------------------------------------------------------------
    def _FrameHelper(self, container, r, c, rs, cs):
        # Frame
        f = tk.LabelFrame(container)

        # Define grid
        for i in range(rs):
            f.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)
        for i in range(cs):
            f.columnconfigure(i, minsize=self.COL_SIZE, weight=0)

        # Place frame
        f.grid(row=r, column=c, rowspan=rs, columnspan=cs, sticky='nesw')

        return f

    # -------------------------------------------------------------------------
    def _BindEvents(self):
        self.assCatBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateCategories(
                event,
                self.assCatBox,
                self.assSelBox,
                self.assDic,
                'ass'
                )
            )

        self.incCatBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateCategories(
                event,
                self.incCatBox,
                self.incSelBox,
                self.incDic,
                'inc'
                )
            )

        self.liaCatBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateCategories(
                event,
                self.liaCatBox,
                self.liaSelBox,
                self.liaDic,
                'lia'
                )
            )

        self.expCatBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateCategories(
                event,
                self.expCatBox,
                self.expSelBox,
                self.expDic,
                'exp'
                )
            )

        self.assSelBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateSelections(
                event,
                self.assSelBox,
                self.assDic,
                self.curAssCat,
                'ass'
                )
            )

        self.incSelBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateSelections(
                event,
                self.incSelBox,
                self.incDic,
                self.curIncCat,
                'inc'
                )
            )

        self.liaSelBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateSelections(
                event,
                self.liaSelBox,
                self.liaDic,
                self.curLiaCat,
                'lia'
                )
            )

        self.expSelBox.bind('<ButtonRelease-1>',
            lambda event: self._UpdateSelections(
                event,
                self.expSelBox,
                self.expDic,
                self.curExpCat,
                'exp'
                )
            )

        self.root.bind('<<NotebookTabChanged>>', self._TabChanged)

    # -------------------------------------------------------------------------
    def _AddSplitRow(self):
        rowIndex = len(self.rows)

        line = tk.Label(self.scrollFrame, text=rowIndex)
        line.grid(
            row        =rowIndex,
            column     =0,
            rowspan    =1,
            columnspan =1,
            sticky     ='w'
        )

        # Account
        acctStr = tk.StringVar(value='')
        acctBox = ttk.Combobox(
            self.scrollFrame,
            textvariable    =acctStr,
            font            =FONT_BOXES,
            width           =11*WSCALE,
            state           ='readonly',
            postcommand     =self._CanvasScrollStop
        )
        acctBox.grid(
            row             =rowIndex,
            column          =1,
            rowspan         =1,
            columnspan      =11,
            sticky          ='w',
        )

        # Memo
        memoStr = tk.StringVar(value='')
        memoBox = tk.Entry(
            self.scrollFrame,
            textvariable    =memoStr,
            font            =FONT_BOXES,
            width           =11*WSCALE,
            justify         ='left'
        )
        memoBox.grid(
            row             =rowIndex,
            column          =13,
            sticky          ='w',
            rowspan         =1,
            columnspan      =11
        )

        # Amount
        amntStr = tk.StringVar(value='')
        amntBox = tk.Entry(
            self.scrollFrame,
            textvariable    =amntStr,
            font            =FONT_BOXES,
            width           =3*WSCALE,
            justify         ='left'
        )
        amntBox.grid(
            row             =rowIndex,
            column          =25,
            sticky          ='w',
            rowspan         =1,
            columnspan      =3
        )

        # If this is the first row, make it readonly
        if (rowIndex == 0):
            acctBox.configure(state='disabled')
            memoBox.configure(state='readonly')
            amntBox.configure(state='readonly')

        # Prevent scrolling while hovering
        acctBox.bind('<MouseWheel>', self._StopScrollOnHover)

        # Resume scroll if acct selected
        acctBox.bind('<<ComboboxSelected>>', self._CanvasScrollStart)

        # Resume scroll if dropdown closed / arrow pressed
        acctBox.bind('<ButtonRelease-1>', self._CanvasScrollStart)

        # TODO - figure out a way to resume scroll when user clicks away

        self.rows.append((line, acctStr, acctBox, memoStr, memoBox, amntStr, amntBox))

        # Reset the view
        self.canvas.yview_moveto(0)

    # -------------------------------------------------------------------------
    def _DeleteSplitRow(self):
        rowIndex = len(self.rows)

        if (rowIndex > 2):
            l, acctS, acctB, mS, mB, amntS, amntB = self.rows.pop(rowIndex-1)
            l.destroy()
            mB.destroy()
            acctB.destroy()
            amntB.destroy()

    # -------------------------------------------------------------------------
    def ResetSplitRows(self):
        rowIndex = len(self.rows)

        for i in range(rowIndex,0,-1):
            l, acctS, acctB, mS, mB, amntS, amntB = self.rows.pop(i-1)
            l.destroy()
            mB.destroy()
            acctB.destroy()
            amntB.destroy()

        # Create first three rows in split tab
        for _ in range(3):
            self._AddSplitRow()

    # -------------------------------------------------------------------------
    def _CanvasScrollStop(self):
        self.stopScroll = True

    # -------------------------------------------------------------------------
    def _CanvasScrollStart(self, event):
        self.stopScroll = False

    # -------------------------------------------------------------------------
    def _StopScrollOnHover(self, event):
        return 'break'

    # -------------------------------------------------------------------------
    def _TabChanged(self, event):
        # Reset view in split tap
        self.canvas.yview_moveto(0)

    # -------------------------------------------------------------------------
    def _LoadAccounts(self, catBox: tk.Text, selBox: tk.Text, dic: dict):
        ''' Helper to load accounts into boxes for first time '''
        # Clear boxes
        catBox.delete('1.0', 'end')
        selBox.delete('1.0', 'end')

        # Default to selecting first category
        firstCat = next(iter(dic))

        # Load categories
        for cat in dic.keys():
            if (cat == firstCat):
                catBox.insert('end', cat, 'selected')
            else:
                catBox.insert('end', cat)

            catBox.insert('end', '\n')

        # Load accounts
        for item in dic[firstCat]:
            item = item + '\n'
            selBox.insert('end', item)

    # -------------------------------------------------------------------------
    def _ClearSelections(self, skip=''):
        if (skip != 'ass'):
            self.assSelBox.delete('1.0', 'end')
            for acct in self.assDic[self.curAssCat]:
                self.assSelBox.insert('end', acct)
                self.assSelBox.insert('end', '\n')

        if (skip != 'inc'):
            self.incSelBox.delete('1.0', 'end')
            for acct in self.incDic[self.curIncCat]:
                self.incSelBox.insert('end', acct)
                self.incSelBox.insert('end', '\n')

        if (skip != 'lia'):
            self.liaSelBox.delete('1.0', 'end')
            for acct in self.liaDic[self.curLiaCat]:
                self.liaSelBox.insert('end', acct)
                self.liaSelBox.insert('end', '\n')

        if (skip != 'exp'):
            self.expSelBox.delete('1.0', 'end')
            for acct in self.expDic[self.curExpCat]:
                self.expSelBox.insert('end', acct)
                self.expSelBox.insert('end', '\n')

    # -------------------------------------------------------------------------
    def _UpdateCategories(self, event, catBox, selBox, dic, who):
        # Get selected category
        selCat = catBox.get("insert linestart", "insert lineend")

        if (selCat == ''):
            return

        # Clear both the category box and selection box
        catBox.delete('1.0', 'end')
        selBox.delete('1.0', 'end')

        # Rewrite category with selection bold
        for cat in dic.keys():
            if (cat == selCat):
                catBox.insert('end', cat, 'selected')
            else:
                catBox.insert('end', cat)

            catBox.insert('end', '\n')

        # Rewrite the new option to the selection box
        for item in dic[selCat]:
            item = item + '\n'
            selBox.insert('end', item)

        # Update current category
        if (who == 'ass'):
            self.curAssCat = selCat
        if (who == 'inc'):
            self.curIncCat = selCat
        if (who == 'lia'):
            self.curLiaCat = selCat
        if (who == 'exp'):
            self.curExpCat = selCat

    # -------------------------------------------------------------------------
    def _UpdateSelections(self, event, selBox, dic, curCat, who):
        # Get selected account
        selAcct = selBox.get("insert linestart", "insert lineend")

        if (selAcct == ''):
            return

        # Clear the selection box
        selBox.delete('1.0', 'end')

        # Rewrite the new options with selection bold
        for acct in dic[curCat]:
            if (acct == selAcct):
                selBox.insert('end', acct, 'selected')
            else:
                selBox.insert('end', acct)

            selBox.insert('end', '\n')

        # Clear other selections
        self._ClearSelections(skip=who)

        # Update the selected account
        acct = ''
        if (who == 'ass'):
            acct = 'Assets'
        if (who == 'inc'):
            acct = 'Income'
        if (who == 'lia'):
            acct = 'Liabilities'
        if (who == 'exp'):
            acct = 'Expenses'

        acct = acct + ':' + curCat + ':' + selAcct
        self.selectedAcct = acct

    # -------------------------------------------------------------------------
    def _UpdateSimple(self, acctNameFull):
        # Get category
        tmp = acctNameFull.split(':')
        selCat = tmp[1]

        # Get account
        selAcct = acctNameFull.rpartition(':')[-1]

        if ('Assets:' in acctNameFull):
            who = 'ass'
            catBox = self.assCatBox
            selBox = self.assSelBox
            dic = self.assDic
            self.curAssCat = selCat
        if ('Income:' in acctNameFull):
            who = 'inc'
            catBox = self.incCatBox
            selBox = self.incSelBox
            dic = self.incDic
            self.curIncCat = selCat
        if ('Liabilities:' in acctNameFull):
            who = 'lia'
            catBox = self.liaCatBox
            selBox = self.liaSelBox
            dic = self.liaDic
            self.curLiaCat = selCat
        if ('Expenses:' in acctNameFull):
            who = 'exp'
            catBox = self.expCatBox
            selBox = self.expSelBox
            dic = self.expDic
            self.curExpCat = selCat

        # Clear both the category box and selection box
        catBox.delete('1.0', 'end')
        selBox.delete('1.0', 'end')

        # Rewrite category with selection bold
        for cat in dic.keys():
            if (cat == selCat):
                catBox.insert('end', cat, 'selected')
            else:
                catBox.insert('end', cat)

            catBox.insert('end', '\n')

        # Rewrite the new options with selection bold
        for acct in dic[selCat]:
            if (acct == selAcct):
                selBox.insert('end', acct, 'selected')
            else:
                selBox.insert('end', acct)

            selBox.insert('end', '\n')

        # Clear other selections
        self._ClearSelections(skip=who)

        # Update the selected account
        self.selectedAcct = acctNameFull

        # Clear memo
        self.memo.set('')

    # # -------------------------------------------------------------------------
    # def _UpdateSplit(self, entry):
    #     for mS, mB, acctS, acctB, amntS, amntB in self.rows:
    #         acctB['values'] = list

    # -------------------------------------------------------------------------
    def LoadImportDropdown(self, list):
        self.importDropdown['values'] = list

    # -------------------------------------------------------------------------
    def LoadSplitAcctDropdowns(self, list):
        self.fullAcctList = list

        for l, acctS, acctB, mS, mB, amntS, amntB in self.rows:
            acctB['values'] = list

    # -------------------------------------------------------------------------
    def LoadAssAcctDropdown(self, list):
        self.assAcctDropdown['values'] = list

    # -------------------------------------------------------------------------
    def LoadAssets(self, dic):
        self._LoadAccounts(self.assCatBox, self.assSelBox, dic)

        firstCat = next(iter(dic))
        self.curAssCat = firstCat
        self.assDic = dic

    # -------------------------------------------------------------------------
    def LoadIncome(self, dic):
        self._LoadAccounts(self.incCatBox, self.incSelBox, dic)

        firstCat = next(iter(dic))
        self.incDic = dic
        self.curIncCat = firstCat

    # -------------------------------------------------------------------------
    def LoadLiabilities(self, dic):
        self._LoadAccounts(self.liaCatBox, self.liaSelBox, dic)

        firstCat = next(iter(dic))
        self.liaDic = dic
        self.curLiaCat = firstCat

    # -------------------------------------------------------------------------
    def LoadExpenses(self, dic):
        self._LoadAccounts(self.expCatBox, self.expSelBox, dic)

        firstCat = next(iter(dic))
        self.expDic = dic
        self.curExpCat = firstCat

    # -------------------------------------------------------------------------
    def Log(self, txt, tag='default'):
        '''
        Logs information to GUI preview box

        '''
        if (txt == ' '):
            # Blank log means delete log
            self.previewBox.delete('1.0', 'end')
            return

        self.previewBox.insert('end', txt, tag)
        self.previewBox.insert('end', '\n', tag)

    # -------------------------------------------------------------------------
    def Update(self, entry: Entry):
        if ((entry.split == False) and (entry.size == 2)):
            acct = entry[1].acctF
            if (acct != ''):
                self._UpdateSimple(acct)
        elif (entry.split == True):
            self._UpdateSplit(entry)

        # Update log box
        self.Log(' ')
        txt = entry.GetHeader()
        self.Log(txt, 'header')
        txt = entry.GetDataAsText()
        self.Log(txt, 'default')

    # -------------------------------------------------------------------------
    def _HandleConfigureEvent(self, event):
        if (self.stopScroll == True):
            return
        self.canvas.configure(scrollregion=self.canvas.bbox(self.scrollFrameId))

    # -------------------------------------------------------------------------
    def _HandleMouseWheelEvent(self, event):
        if (self.stopScroll == True):
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

