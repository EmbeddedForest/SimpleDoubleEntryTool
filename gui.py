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
# TODO:
#   - Clean up GUI initializations to make more flexible to changes
#
#------------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


# Generic Fonts
FONT_TITLE = ('Calibri', 36, 'bold italic')
FONT_FRAME = ('Calibri', 11, 'italic')
FONT_LABEL = ('Calibri', 14, 'bold')
FONT_BOXES = ('Calibri', 11)
FONT_NOTES = ('Calibri', 9)

# Static Frame Labels
FRAMES = \
[
    ('Setup',           FONT_FRAME, (1,  24), (5,  26), 'nesw'),
    ('Date',            FONT_FRAME, (8,   1), (5,  25), 'nesw'),
    ('Split',           FONT_FRAME, (8,  27), (11, 23), 'nesw'),
    ('Select Account',  FONT_FRAME, (14,  1), (13, 25), 'nesw'),
    ('Log Box',         FONT_FRAME, (28, 12), (10, 38), 'nesw'),
    ('Opening Balance', FONT_FRAME, (20, 27), (7,  23), 'nesw')
]

# Static Labels
LABELS = \
[
    # Title
    ('Simple Double Entry Tool', FONT_TITLE, (1,   5), (5,  18), 'nesw'),

    # Setup Frame
    ('Import File:',             FONT_LABEL, (2,  24), (1,   5),    'e'),
    ('Asscociated Acct:',        FONT_LABEL, (4,  24), (1,   5),    'e'),

    # Data Frame
    ('Date:',                    FONT_LABEL, (9,   2), (1,   3),    'w'),
    ('Description:',             FONT_LABEL, (9,   6), (1,  15),    'w'),
    ('Amount:',                  FONT_LABEL, (9,  22), (1,   3),    'w'),

    # Account Frame
    ('Expense:',                 FONT_LABEL, (16,  1), (1,   4),    'e'),
    ('Liability:',               FONT_LABEL, (18,  1), (1,   4),    'e'),
    ('Income:',                  FONT_LABEL, (20,  1), (1,   4),    'e'),
    ('Asset:',                   FONT_LABEL, (22,  1), (1,   4),    'e'),
    ('Memo:',                    FONT_LABEL, (24,  1), (1,   4),    'e'),

    # Split Frame
    ('Account:',                 FONT_LABEL, (10, 27), (1,   4),    'e'),
    ('Memo:',                    FONT_LABEL, (12, 27), (1,   4),    'e'),
    ('Amount:',                  FONT_LABEL, (14, 27), (1,   4),    'e'),
    ('(Negative = Credit)',      FONT_NOTES, (14, 35), (1,  15),    'w'),

    # Opening Balance
    ('Account:',                 FONT_LABEL, (22, 27), (1,   4),    'e'),
    ('Amount:',                  FONT_LABEL, (24, 27), (1,   4),    'e'),
    ('Date:',                    FONT_LABEL, (24, 35), (1,   4),    'e'),
]


class MyGui():
    ''' Class to hold all GUI functionality '''

    # Constrain sizes to make GUI deisgn more simple
    NUM_COLS = 51
    NUM_ROWS = 39
    COL_SIZE = 30
    ROW_SIZE = 24


    def __init__(self):
        self.root = tk.Tk()
        self._BuildGui()


    def _AddStaticFrames(self):
        ''' Add all static label frames to GUI '''
        for frame in FRAMES:
            tmp = tk.LabelFrame(
                self.root,
                text       =frame[0],
                font       =frame[1]
            )

            tmp.grid(
                row        =frame[2][0],
                column     =frame[2][1],
                rowspan    =frame[3][0],
                columnspan =frame[3][1],
                sticky     =frame[4]
            )


    def _AddStaticLabels(self):
        ''' Add all static labels to GUI '''
        for label in LABELS:
            tmp = tk.Label(
                self.root,
                text       =label[0],
                font       =label[1]
            )

            tmp.grid(
                row        =label[2][0],
                column     =label[2][1],
                rowspan    =label[3][0],
                columnspan =label[3][1],
                sticky     =label[4]
            )


    def _BuildGui(self):
        root = self.root

        # Application Title
        root.title('EmbeddedForest')

        # Define GUI grid
        for i in range(self.NUM_COLS):
            root.columnconfigure(i, minsize=self.COL_SIZE, weight=2)
        for i in range(self.NUM_ROWS):
            root.rowconfigure(i, minsize=self.ROW_SIZE, weight=2)

        self._AddStaticFrames()
        self._AddStaticLabels()


        #----------------------------------------------------------------------
        # Logo
        #----------------------------------------------------------------------
        self.logo = ImageTk.PhotoImage(Image.open('tree.png'))
        tmp = tk.Label(root, image=self.logo)
        tmp.grid(row=1, column=1, sticky='nesw', rowspan=5, columnspan=4)


        #----------------------------------------------------------------------
        # Setup Frame
        #----------------------------------------------------------------------
        # Import Dropdown
        self.selectedImportFile = tk.StringVar()
        self.importDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedImportFile,
            font            =FONT_BOXES,
            width           =60
        )
        self.importDropdown.grid(
            row             =2,
            column          =29,
            sticky          ='w',
            rowspan         =1,
            columnspan      =14
        )

        # Associated Account Dropdown
        self.selectedAssAcct = tk.StringVar()
        self.assAcctDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedAssAcct,
            font            =FONT_BOXES,
            width           =60
        )
        self.assAcctDropdown.grid(
            row             =4,
            column          =29,
            sticky          ='w',
            rowspan         =1,
            columnspan      =14
        )

        # Start Button
        self.startButton = tk.Button(
            root,
            text        ='Start',
            font        =FONT_LABEL
        )
        self.startButton.grid(
            row         =2,
            column      =43,
            sticky      ='nesw',
            padx        =20,
            pady        =20,
            rowspan     =3,
            columnspan  =6
        )


        #----------------------------------------------------------------------
        # Data Frame
        #----------------------------------------------------------------------
        # Date Box
        self.displayDate = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.displayDate,
            font            =FONT_BOXES,
            width           =12,
            justify         ='center',
            state           ='readonly'
        )
        tmp.grid(
            row             =10,
            column          =2,
            sticky          ='w',
            rowspan         =1,
            columnspan      =3
        )

        # Description Box
        self.displayDescription = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.displayDescription,
            font            =FONT_BOXES,
            width           =64,
            justify         ='left',
            state           ='readonly'
        )
        tmp.grid(
            row             =10,
            column          =6,
            sticky          ='w',
            rowspan         =1,
            columnspan      =15
        )

        # Amount Box
        self.displayAmount = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.displayAmount,
            font            =FONT_BOXES,
            width           =12,
            justify         ='center',
            state           ='readonly'
        )
        tmp.grid(
            row             =10,
            column          =22,
            sticky          ='w',
            rowspan         =1,
            columnspan      =3
        )

        # Transaction Counter Label
        self.transCount = tk.StringVar(value=' ')
        tmp = tk.Label(
            root,
            textvariable    =self.transCount,
            font            =FONT_NOTES
        )
        tmp.grid(
            row             =12,
            column          =2,
            sticky          ='w',
            rowspan         =1,
            columnspan      =24
        )

        #----------------------------------------------------------------------
        # Account Frame
        #----------------------------------------------------------------------
        # Expenses Dropdown
        self.selectedExpense = tk.StringVar()
        self.expenseDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedExpense,
            font            =FONT_BOXES,
            width           =80
        )
        self.expenseDropdown.grid(
            row             =16,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =20
        )

        # Liability Dropdown
        self.selectedLiability = tk.StringVar()
        self.liabilityDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedLiability,
            font            =FONT_BOXES,
            width           =80
        )
        self.liabilityDropdown.grid(
            row             =18,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =20
        )

        # Income Dropdown
        self.selectedIncome = tk.StringVar()
        self.incomeDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedIncome,
            font            =FONT_BOXES,
            width           =80
        )
        self.incomeDropdown.grid(
            row             =20,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =20
        )

        # Asset Dropdown
        self.selectedAsset = tk.StringVar()
        self.assetDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedAsset,
            font            =FONT_BOXES,
            width           =80
        )
        self.assetDropdown.grid(
            row             =22,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =20
        )

        # Memo Box
        self.memo = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.memo,
            font            =FONT_NOTES,
            width           =95,
            justify         ='left'
        )
        tmp.grid(
            row             =24,
            column          =5,
            sticky          ='w',
            rowspan         =1,
            columnspan      =20
        )


        #----------------------------------------------------------------------
        # Split Frame
        #----------------------------------------------------------------------
        # Split Account Dropdown
        self.selectedSplitAcct = tk.StringVar()
        self.splitAcctDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedSplitAcct,
            font            =FONT_BOXES,
            width           =74
        )
        self.splitAcctDropdown.grid(
            row             =10,
            column          =31,
            sticky          ='w',
            rowspan         =1,
            columnspan      =18
        )

        # Split Memo Box
        self.splitMemo = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.splitMemo,
            font            =FONT_NOTES,
            width           =87,
            justify         ='left'
        )
        tmp.grid(
            row             =12,
            column          =31,
            sticky          ='w',
            rowspan         =1,
            columnspan      =18
        )

        # Split Amount Box
        self.splitAmnt = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.splitAmnt,
            font            =FONT_NOTES,
            width           =16,
            justify         ='left'
        )
        tmp.grid(
            row             =14,
            column          =31,
            sticky          ='w',
            rowspan         =1,
            columnspan      =48
        )

        # Add Split Button
        self.addSplitButton = tk.Button(
            root,
            text        ='Add Split',
            font        =FONT_LABEL
        )
        self.addSplitButton.grid(
            row         =16,
            column      =32,
            sticky      ='nesw',
            padx        =20,
            pady        =0,
            rowspan     =2,
            columnspan  =5
        )

        # Undo Split Button
        self.undoSplitButton = tk.Button(
            root,
            text        ='Undo',
            font        =FONT_LABEL
        )
        self.undoSplitButton.grid(
            row         =16,
            column      =40,
            sticky      ='nesw',
            padx        =20,
            pady        =0,
            rowspan     =2,
            columnspan  =5
        )


        #----------------------------------------------------------------------
        # Opening Balance Frame
        #----------------------------------------------------------------------
        # Opening Balance Account Dropdown
        self.selectedOpenAcct = tk.StringVar()
        self.openAcctDropdown = ttk.Combobox(
            root,
            textvariable    =self.selectedOpenAcct,
            font            =FONT_BOXES,
            width           =74
        )
        self.openAcctDropdown.grid(
            row             =22,
            column          =31,
            sticky          ='w',
            rowspan         =1,
            columnspan      =18
        )

        # Opening Balance Amount Box
        self.openAmnt = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.openAmnt,
            font            =FONT_NOTES,
            width           =16,
            justify         ='left'
        )
        tmp.grid(
            row             =24,
            column          =31,
            sticky          ='w',
            rowspan         =1,
            columnspan      =48
        )

        # Opening Balance Date Box
        self.openDate = tk.StringVar(value=' ')
        tmp = tk.Entry(
            root,
            textvariable    =self.openDate,
            font            =FONT_NOTES,
            width           =16,
            justify         ='left'
        )
        tmp.grid(
            row             =24,
            column          =39,
            sticky          ='w',
            rowspan         =1,
            columnspan      =48
        )

        # Add Opening Balance Button
        self.undoSplitButton = tk.Button(
            root,
            text        ='Add',
            font        =FONT_LABEL
        )
        self.undoSplitButton.grid(
            row         =23,
            column      =44,
            sticky      ='nesw',
            padx        =20,
            pady        =20,
            rowspan     =3,
            columnspan  =5
        )


        #----------------------------------------------------------------------
        # Log Frame
        #----------------------------------------------------------------------
        # Log box
        self.logBox = tk.Text(
            root,
            font        =FONT_NOTES,
            width       =170,
            height      =15
        )
        self.logBox.grid(
            row         =29,
            column      =13,
            sticky      ='nsew',
            rowspan     =8,
            columnspan  =36
        )

        # Scroll bar for log box
        logScroll = tk.Scrollbar(
            root,
            orient      ='vertical',
            command     =self.logBox.yview
        )
        self.logBox.configure(yscrollcommand=logScroll.set)
        logScroll.grid(
            row         =29,
            column      =49,
            sticky      ='wns',
            padx        =0,
            pady        =0,
            rowspan=8
        )

        # Tags for different text types for log box
        self.logBox.tag_configure(
            'header',
            background  ='white',
            foreground  ='black',
            font        =('consolas', 10, 'bold')
        )
        self.logBox.tag_configure(
            'default',
            background  ='white',
            foreground  ='black',
            font        =('consolas', 10)
        )
        self.logBox.tag_configure(
            'error',
            background  ='white',
            foreground  ='red',
            font        =('consolas', 10)
        )

        # Add Entry Button
        self.addEntryButton = tk.Button(
            root,
            text        ='Add to Journal',
            font        =FONT_LABEL
        )
        self.addEntryButton.grid(
            row         =27,
            column      =2,
            sticky      ='nesw',
            padx        =20,
            pady        =20,
            rowspan     =6,
            columnspan  =8
        )

        # Redo Entry Button
        self.addEntryButton = tk.Button(
            root,
            text        ='Redo Last Entry',
            font        =FONT_LABEL
        )
        self.addEntryButton.grid(
            row         =34,
            column      =3,
            sticky      ='nesw',
            padx        =20,
            pady        =20,
            rowspan     =2,
            columnspan  =6
        )


    def LoadImportDropdown(self, list):
         ''' Loads import dropdown combobox '''
         self.importDropdown['values'] = list


    def LoadAssAcctDropdown(self, list):
         ''' Loads associated account dropdown combobox '''
         self.assAcctDropdown['values'] = list


    def Log(self, payload):
        '''
        Logs information to GUI preview box

        payload = (msg, tag)
        '''

        txt = payload[0]
        tag = payload[1]

        if (txt == ' '):
            # Blank log means delete log
            self.logBox.delete('1.0', 'end')
            return

        self.logBox.insert('end', txt, tag)
        self.logBox.insert('end', '\n', tag)