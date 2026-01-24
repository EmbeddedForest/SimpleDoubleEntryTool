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
            text = frame[0]
            font = frame[1]
            r    = frame[2][0]
            c    = frame[2][1]
            rs   = frame[3][0]
            cs   = frame[3][1]
            s    = frame[4]

            t = tk.LabelFrame(self.root, text=text, font=font)
            t.grid(row=r, column=c, sticky=s, rowspan=rs, columnspan=cs)


    def _AddStaticLabels(self):
        ''' Add all static labels to GUI '''

        for label in LABELS:
            text = label[0]
            font = label[1]
            r    = label[2][0]
            c    = label[2][1]
            rs   = label[3][0]
            cs   = label[3][1]
            s    = label[4]

            t = tk.Label(self.root, text=text, font=font)
            t.grid(row=r, column=c, sticky=s, rowspan=rs, columnspan=cs)


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

        # Logo
        tkLogo = ImageTk.PhotoImage(Image.open('tree.png'))
        temp = tk.Label(root, image=tkLogo)
        temp.image = tkLogo     # This is the only way to make image work properly
        temp.grid(row=1, column=2, sticky='nesw', padx=0, pady=0, rowspan=5, columnspan=4)

        # Dynamic Labels
        lableTextTransCount = tk.StringVar(value='(Transaction 0 of 0 in spreadsheet.csv)')
        temp = tk.Label(root, textvariable=lableTextTransCount, font=('Calibri', 9))
        temp.grid(row=12, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=24)
        # lableTextTransCount.set('NEW TEXT')

        # Data display boxes
        self.displayDate = tk.StringVar(value='12/12/2025')
        temp = tk.Entry(root, textvariable=self.displayDate, font=('Calibri', 11), width=12, justify='center', state='readonly')
        temp.grid(row=10, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        self.displayDescription = tk.StringVar(value='  COMPANY INC PAYROLL')
        temp = tk.Entry(root, textvariable=self.displayDescription, font=('Calibri', 11), width=64, justify='left', state='readonly')
        temp.grid(row=10, column=6, sticky='w', padx=0, pady=0, rowspan=1, columnspan=15)

        self.displayAmount = tk.StringVar(value='420.69')
        temp = tk.Entry(root, textvariable=self.displayAmount, font=('Calibri', 11), width=12, justify='center', state='readonly')
        temp.grid(row=10, column=22, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        # Selection boxes
        self.selectionExpenses = tk.StringVar()
        self.expensesDropdown = ttk.Combobox(root, textvariable=self.selectionExpenses, font=('Calibri', 11), width=80)
        self.expensesDropdown.grid(row=16, column=5, sticky='w', rowspan=1, columnspan=20)

        self.selectionLiability = tk.StringVar()
        self.liabilityDropdown = ttk.Combobox(root, textvariable=self.selectionLiability, font=('Calibri', 11), width=80)
        self.liabilityDropdown.grid(row=18, column=5, sticky='w', rowspan=1, columnspan=20)

        self.selectionIncome = tk.StringVar()
        self.incomeDropdown = ttk.Combobox(root, textvariable=self.selectionIncome, font=('Calibri', 11), width=80)
        self.incomeDropdown.grid(row=20, column=5, sticky='w', rowspan=1, columnspan=20)

        self.selectionAsset = tk.StringVar()
        self.assetDropdown = ttk.Combobox(root, textvariable=self.selectionAsset, font=('Calibri', 11), width=80)
        self.assetDropdown.grid(row=22, column=5, sticky='w', rowspan=1, columnspan=20)

        self.selectedImportFile = tk.StringVar()
        self.importDropdown = ttk.Combobox(root, textvariable=self.selectedImportFile, font=('Calibri', 11), width=60)
        self.importDropdown.grid(row=2, column=29, sticky='w', rowspan=1, columnspan=14)

        self.selectedAssAcct = tk.StringVar()
        self.assAcctDropdown = ttk.Combobox(root, textvariable=self.selectedAssAcct, font=('Calibri', 11), width=60)
        self.assAcctDropdown.grid(row=4, column=29, sticky='w', rowspan=1, columnspan=14)

        selectionJournal = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionJournal, font=('Calibri', 11), width=72)
        temp.grid(row=10, column=31, sticky='w', rowspan=1, columnspan=18)

        # Input boxes
        self.memo = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=self.memo, font=('Calibri', 11), width=82, justify='left')
        temp.grid(row=24, column=5, sticky='w', padx=0, pady=0, rowspan=1, columnspan=20)

        inputMemo = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputMemo, font=('Calibri', 11), width=74, justify='left')
        temp.grid(row=12, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=18)

        inputAmount = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputAmount, font=('Calibri', 11), width=16, justify='left')
        temp.grid(row=14, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=4)

        # Log box
        self.logBox = tk.Text(root, font=('Consolas', 9), width=170, height=15)
        self.logBox.grid(row=29, column=13, sticky='nsew', padx=0, pady=0, rowspan=8, columnspan=36)

        # Scroll bar for log box
        logScroll = tk.Scrollbar(root, orient='vertical', command=self.logBox.yview)
        self.logBox.configure(yscrollcommand=logScroll.set)
        logScroll.grid(row=29, column=49, sticky='wns', padx=0, pady=0, rowspan=8)

        # Tags for different text types
        self.logBox.tag_configure('header', background='white', foreground='black', font=('consolas', 10, 'bold'))
        self.logBox.tag_configure('default', background='white', foreground='black', font=('consolas', 10))
        self.logBox.tag_configure('error', background='white', foreground='red', font=('consolas', 10))



        # Buttons
        self.startButton = tk.Button(root, text='Start', font=('Calibri', 14, 'bold'))
        self.startButton.grid(row=2, column=43, sticky='nesw', padx=20, pady=20, rowspan=3, columnspan=6)

        self.addSplitButton = tk.Button(root, text='Add Split', font=('Calibri', 14, 'bold'))
        self.addSplitButton.grid(row=16, column=32, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

        self.undoSplitButton = tk.Button(root, text='Undo', font=('Calibri', 14, 'bold'))
        self.undoSplitButton.grid(row=16, column=40, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

        self.addEntryButton = tk.Button(root, text='Add to Ledger', font=('Calibri', 14, 'bold'))
        self.addEntryButton.grid(row=27, column=2, sticky='nesw', padx=20, pady=20, rowspan=6, columnspan=8)

        self.redoEntryButton = tk.Button(root, text='Redo Last Entry', font=('Calibri', 14, 'bold'))
        self.redoEntryButton.grid(row=34, column=3, sticky='nesw', padx=20, pady=20, rowspan=2, columnspan=6)


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