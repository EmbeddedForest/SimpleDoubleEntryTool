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


class MyGui():
    ''' Class to hold all GUI functionality '''

    # Constrain sizes to make GUI deisgn more simple
    NUM_COLS = 39
    NUM_ROWS = 41
    COL_SIZE = 30
    ROW_SIZE = 20

    selectedAcct = ''
    simpleEntry = True

    def __init__(self):
        self.root = tk.Tk()
        self._BuildGui()
        self._BindEvents()

    def _BuildGui(self):
        root = self.root

        # Application Title
        root.title('EmbeddedForest')

        # Define root grid
        for i in range(self.NUM_COLS):
            root.columnconfigure(i, minsize=self.COL_SIZE, weight=2)
        for i in range(self.NUM_ROWS):
            root.rowconfigure(i, minsize=self.ROW_SIZE, weight=2)

        #----------------------------------------------------------------------
        # Title Frame
        #----------------------------------------------------------------------
        # Frame
        titleFrame = tk.LabelFrame(
            self.root
        )
        titleFrame.grid(
            row        =1,
            column     =2,
            rowspan    =5,
            columnspan =13,
            sticky     ='nesw'
        )

        # Define grid
        for i in range(13):
            titleFrame.columnconfigure(i, minsize=self.COL_SIZE, weight=0)
        for i in range(5):
            titleFrame.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)

        # Title 1
        tmp = tk.Label(
            titleFrame,
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
            titleFrame,
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
        tmp = tk.Label(titleFrame, image=logo)
        tmp.image = logo
        tmp.grid(row=0, column=0, sticky='nesw', rowspan=5, columnspan=4)


        #----------------------------------------------------------------------
        # Setup Frame
        #----------------------------------------------------------------------
        # Frame
        setupFrame = tk.LabelFrame(
            self.root,
        )
        setupFrame.grid(
            row        =1,
            column     =17,
            rowspan    =5,
            columnspan =21,
            sticky     ='nesw'
        )

        # Define grid
        for i in range(21):
            setupFrame.columnconfigure(i, minsize=self.COL_SIZE, weight=0)
        for i in range(5):
            setupFrame.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)

        # Setup Label
        tmp = tk.Label(
            setupFrame,
            text       ='Setup',
            font       =FONT_FRAME
        )
        tmp.grid(
            row        =0,
            column     =0,
            rowspan    =1,
            columnspan =5,
            sticky     ='w'
        )

        # Import File Label
        tmp = tk.Label(
            setupFrame,
            text       ='Import File:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =1,
            column     =0,
            rowspan    =1,
            columnspan =5,
            sticky     ='e'
        )

        # Associated Account Label
        tmp = tk.Label(
            setupFrame,
            text       ='Associated Account:',
            font       =FONT_LABEL
        )
        tmp.grid(
            row        =3,
            column     =0,
            rowspan    =1,
            columnspan =5,
            sticky     ='e'
        )

        # Import Dropdown
        self.selectedImportFile = tk.StringVar()
        self.importDropdown = ttk.Combobox(
            setupFrame,
            textvariable    =self.selectedImportFile,
            font            =FONT_BOXES,
            width           =44,
            state           ='readonly'
        )
        self.importDropdown.grid(
            row             =1,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =11
        )

        # Associated Account Dropdown
        self.selectedAssAcct = tk.StringVar()
        self.assAcctDropdown = ttk.Combobox(
            setupFrame,
            textvariable    =self.selectedAssAcct,
            font            =FONT_BOXES,
            width           =44,
            state           ='readonly'
        )
        self.assAcctDropdown.grid(
            row             =3,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =11
        )

        # Start Button
        self.startButton = tk.Button(
            setupFrame,
            text        ='Start',
            font        =FONT_LABEL
        )
        self.startButton.grid(
            row         =1,
            column      =16,
            sticky      ='nesw',
            padx        =20,
            pady        =10,
            rowspan     =3,
            columnspan  =5
        )


        #----------------------------------------------------------------------
        # Data Frame
        #----------------------------------------------------------------------
        # Frame
        dataFrame = tk.LabelFrame(
            self.root,
            borderwidth=5
        )
        dataFrame.grid(
            row        =8,
            column     =7,
            rowspan    =4,
            columnspan =25,
            sticky     ='nesw'
        )

        # Define grid
        for i in range(25):
            dataFrame.columnconfigure(i, minsize=self.COL_SIZE, weight=0)
        for i in range(4):
            dataFrame.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)

        # Transaction Data Label
        tmp = tk.Label(
            dataFrame,
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
            dataFrame,
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
            dataFrame,
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
            dataFrame,
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
            dataFrame,
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
            dataFrame,
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
            dataFrame,
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


        #----------------------------------------------------------------------
        # Simple Entry Tab
        #----------------------------------------------------------------------
        # Notebook
        self.notebook = ttk.Notebook(
            self.root
        )
        self.notebook.grid(
            row        =14,
            column     =1,
            rowspan    =13,
            columnspan =37,
            sticky     ='nesw'
        )

        # Simple Entry Tab Frame
        simpleTab = tk.Frame(self.notebook)
        self.notebook.add(simpleTab, text='Simple Entry')

        # Define grid
        for i in range(37):
            simpleTab.columnconfigure(i, minsize=self.COL_SIZE, weight=0)
        for i in range(13):
            simpleTab.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)


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


        #----------------------------------------------------------------------
        # Split Entry Tab
        #----------------------------------------------------------------------
        # Split Tab
        splitTab = tk.Frame(self.notebook)
        self.notebook.add(splitTab, text='Split Entry')


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


        #----------------------------------------------------------------------
        # Preview Frame
        #----------------------------------------------------------------------
        # Frame
        previewFrame = tk.LabelFrame(
            self.root
        )
        previewFrame.grid(
            row        =31,
            column     =1,
            rowspan    =9,
            columnspan =37,
            sticky     ='nesw'
        )

        # Define grid
        for i in range(37):
            previewFrame.columnconfigure(i, minsize=self.COL_SIZE, weight=0)
        for i in range(9):
            previewFrame.rowconfigure(i, minsize=self.ROW_SIZE, weight=0)

        # Preview Label
        tmp = tk.Label(
            previewFrame,
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
            previewFrame,
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
            previewFrame,
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

        # #----------------------------------------------------------------------
        # # Split Frame
        # #----------------------------------------------------------------------
        # # Split Amount Box
        # self.splitAmnt = tk.StringVar(value='')
        # tmp = tk.Entry(
        #     root,
        #     textvariable    =self.splitAmnt,
        #     font            =FONT_NOTES,
        #     width           =16,
        #     justify         ='left'
        # )
        # tmp.grid(
        #     row             =19,
        #     column          =33,
        #     sticky          ='w',
        #     rowspan         =1,
        #     columnspan      =3
        # )

        # # Add Split Button
        # self.addSplitButton = tk.Button(
        #     root,
        #     text        ='Add Split',
        #     font        =FONT_LABEL
        # )
        # self.addSplitButton.grid(
        #     row         =19,
        #     column      =36,
        #     sticky      ='nesw',
        #     padx        =5,
        #     pady        =0,
        #     rowspan     =1,
        #     columnspan  =3
        # )

        # # Undo Split Button
        # self.undoSplitButton = tk.Button(
        #     root,
        #     text        ='Undo',
        #     font        =FONT_LABEL
        # )
        # self.undoSplitButton.grid(
        #     row         =19,
        #     column      =39,
        #     sticky      ='nesw',
        #     padx        =5,
        #     pady        =0,
        #     rowspan     =1,
        #     columnspan  =3
        # )

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


    def _TabChanged(self, event):
        tabIndex = self.notebook.index('current')
        if (tabIndex == 0):
            self.simpleEntry = True
        else:
            self.simpleEntry = False

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

    def UpdateSimple(self, acctNameFull):
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


    def LoadImportDropdown(self, list):
        self.importDropdown['values'] = list

    def LoadAssAcctDropdown(self, list):
        self.assAcctDropdown['values'] = list

    def LoadAssets(self, dic):
        self._LoadAccounts(self.assCatBox, self.assSelBox, dic)

        firstCat = next(iter(dic))
        self.curAssCat = firstCat
        self.assDic = dic

    def LoadIncome(self, dic):
        self._LoadAccounts(self.incCatBox, self.incSelBox, dic)

        firstCat = next(iter(dic))
        self.incDic = dic
        self.curIncCat = firstCat

    def LoadLiabilities(self, dic):
        self._LoadAccounts(self.liaCatBox, self.liaSelBox, dic)

        firstCat = next(iter(dic))
        self.liaDic = dic
        self.curLiaCat = firstCat

    def LoadExpenses(self, dic):
        self._LoadAccounts(self.expCatBox, self.expSelBox, dic)

        firstCat = next(iter(dic))
        self.expDic = dic
        self.curExpCat = firstCat

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

    def Update(self, entry: Entry):
        if ((entry.split == False) and (entry.size == 2)):
            acct = entry[1].acctF
            if (acct != ''):
                self.UpdateSimple(acct)
        elif (entry.split == True):
            self.UpdateSplit(entry)

        # Update log box
        self.Log(' ')
        txt = entry.GetHeader()
        self.Log(txt, 'header')
        txt = entry.GetDataAsText()
        self.Log(txt, 'default')