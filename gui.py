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

    def _BuildGui(self):
        root = self.root

        # Application Title
        self.root.title('EmbeddedForest')

        # Define and build main GUI grid
        for i in range(self.NUM_COLS):
            root.columnconfigure(i, minsize=self.COL_SIZE, weight=1)
        for i in range(self.NUM_ROWS):
            root.rowconfigure(i, minsize=self.ROW_SIZE, weight=1)

        # Add blank labels into first row and column to visually see GUI size
        for x in range(self.NUM_COLS):
                temp = tk.Label(root, text=' ', font=('Segoe UI', 9, 'bold'))
                temp.grid(row=0, column=x, sticky='nesw', padx=0, pady=0)
        for y in range(self.NUM_ROWS):
                temp = tk.Label(root, text=' ', font=('Segoe UI', 9, 'bold'))
                temp.grid(row=y, column=0, sticky='nesw', padx=0, pady=0)

        # Title
        temp = tk.Label(root, text='Simple Double Entry Tool', font=('Calibri', 36, 'bold italic'))
        temp.grid(row=1, column=5, sticky='nesw', padx=0, pady=0, rowspan=5, columnspan=18)

        # Logo
        tkLogo = ImageTk.PhotoImage(Image.open('tree.png'))
        temp = tk.Label(root, image=tkLogo)
        temp.image = tkLogo     # This is the only way to make image work properly
        temp.grid(row=1, column=2, sticky='nesw', padx=0, pady=0, rowspan=5, columnspan=4)

        # Setup Frame
        temp = tk.LabelFrame(root, text='Setup', font=('Calibri', 11, 'italic'))
        temp.grid(row=1, column=24, sticky='nesw', padx=0, pady=0, rowspan=5, columnspan=26)

        # Data Frame
        temp = tk.LabelFrame(root, text='Data', font=('Calibri', 11, 'italic'))
        temp.grid(row=8, column=1, sticky='nesw', padx=0, pady=0, rowspan=5, columnspan=25)

        # Split Frame
        temp = tk.LabelFrame(root, text='Split', font=('Calibri', 11, 'italic'))
        temp.grid(row=8, column=27, sticky='nesw', padx=0, pady=0, rowspan=17, columnspan=23)

        # Account Frame
        temp = tk.LabelFrame(root, text='Select Account', font=('Calibri', 11, 'italic'))
        temp.grid(row=14, column=1, sticky='nesw', padx=0, pady=0, rowspan=11, columnspan=25)

        # Preview Frame
        temp = tk.LabelFrame(root, text='Preview', font=('Calibri', 11, 'italic'))
        temp.grid(row=26, column=12, sticky='nesw', padx=0, pady=0, rowspan=12, columnspan=38)

        # Static Labels - TODO: create function which just runs through a config/table to generate labels
        temp = tk.Label(root, text='Import File:', font=('Calibri', 14, 'bold'))
        temp.grid(row=2, column=24, sticky='e', padx=0, pady=0, rowspan=1, columnspan=5)

        temp = tk.Label(root, text='Asscociated Acct:', font=('Calibri', 14, 'bold'))
        temp.grid(row=4, column=24, sticky='e', padx=0, pady=0, rowspan=1, columnspan=5)

        temp = tk.Label(root, text='Date:', font=('Calibri', 14, 'bold'))
        temp.grid(row=9, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        temp = tk.Label(root, text='Description:', font=('Calibri', 14, 'bold'))
        temp.grid(row=9, column=6, sticky='w', padx=0, pady=0, rowspan=1, columnspan=15)

        temp = tk.Label(root, text='Amount:', font=('Calibri', 14, 'bold'))
        temp.grid(row=9, column=22, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        temp = tk.Label(root, text='Expense:', font=('Calibri', 14, 'bold'))
        temp.grid(row=16, column=1, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Liability:', font=('Calibri', 14, 'bold'))
        temp.grid(row=18, column=1, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Income:', font=('Calibri', 14, 'bold'))
        temp.grid(row=20, column=1, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Asset:', font=('Calibri', 14, 'bold'))
        temp.grid(row=22, column=1, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Account:', font=('Calibri', 14, 'bold'))
        temp.grid(row=10, column=27, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Memo:', font=('Calibri', 14, 'bold'))
        temp.grid(row=12, column=27, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Amount:', font=('Calibri', 14, 'bold'))
        temp.grid(row=15, column=27, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Status:', font=('Calibri', 14, 'bold'))
        temp.grid(row=22, column=27, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='(Negative = Credit = Moving out of selected account)', font=('Calibri', 9))
        temp.grid(row=15, column=35, sticky='w', padx=0, pady=0, rowspan=1, columnspan=15)

        # Dynamic Labels
        lableTextTransCount = tk.StringVar(value='(Transaction 0 of 0 in spreadsheet.csv)')
        temp = tk.Label(root, textvariable=lableTextTransCount, font=('Calibri', 9))
        temp.grid(row=12, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=24)
        # lableTextTransCount.set('NEW TEXT')

        lableTextAutoAccount = tk.StringVar(value='(Account auto-populated based on previous entry)')
        temp = tk.Label(root, textvariable=lableTextAutoAccount, font=('Calibri', 9))
        temp.grid(row=24, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=24)
        # lableTextAutoAccount.set('NEW TEXT')

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

        displaySplitStatus = tk.StringVar(value='  SPLIT NOT BALANCED')
        temp = tk.Entry(root, textvariable=displaySplitStatus, font=('Calibri', 11), width=72, justify='left', state='readonly')
        temp.grid(row=22, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=18)

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
        inputMemo = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputMemo, font=('Calibri', 11), width=72, justify='left')
        temp.grid(row=12, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=18)

        inputAmount = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputAmount, font=('Calibri', 11), width=16, justify='left')
        temp.grid(row=15, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=4)

        # Log box
        self.logBox = tk.Text(root, font=('Consolas', 9), width=170, height=15)
        self.logBox.grid(row=27, column=13, sticky='nsew', padx=0, pady=0, rowspan=10, columnspan=36)

        # Scroll bar for log box
        logScroll = tk.Scrollbar(root, orient='vertical', command=self.logBox.yview)
        self.logBox.configure(yscrollcommand=logScroll.set)
        logScroll.grid(row=27, column=49, sticky='wns', padx=0, pady=0, rowspan=10)

        # Tags for different text types
        self.logBox.tag_configure('header', background='white', foreground='black', font=('consolas', 10, 'bold'))
        self.logBox.tag_configure('default', background='white', foreground='black', font=('consolas', 10))
        self.logBox.tag_configure('error', background='white', foreground='red', font=('consolas', 10))



        # Buttons
        self.startButton = tk.Button(root, text='Start', font=('Calibri', 14, 'bold'))
        self.startButton.grid(row=2, column=43, sticky='nesw', padx=20, pady=20, rowspan=3, columnspan=6)

        self.addSplitButton = tk.Button(root, text='Add Split', font=('Calibri', 14, 'bold'))
        self.addSplitButton.grid(row=18, column=32, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

        self.undoSplitButton = tk.Button(root, text='Undo', font=('Calibri', 14, 'bold'))
        self.undoSplitButton.grid(row=18, column=40, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

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