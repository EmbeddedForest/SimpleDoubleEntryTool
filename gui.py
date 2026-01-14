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
        temp.grid(row=2, column=24, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

        temp = tk.Label(root, text='Journal File:', font=('Calibri', 14, 'bold'))
        temp.grid(row=4, column=24, sticky='e', padx=0, pady=0, rowspan=1, columnspan=4)

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
        displayDate = tk.StringVar(value='12/12/2025')
        temp = tk.Entry(root, textvariable=displayDate, font=('Calibri', 11), width=12, justify='center', state='readonly')
        temp.grid(row=10, column=2, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        displayDescription = tk.StringVar(value='  COMPANY INC PAYROLL')
        temp = tk.Entry(root, textvariable=displayDescription, font=('Calibri', 11), width=64, justify='left', state='readonly')
        temp.grid(row=10, column=6, sticky='w', padx=0, pady=0, rowspan=1, columnspan=15)

        displayAmount = tk.StringVar(value='420.69')
        temp = tk.Entry(root, textvariable=displayAmount, font=('Calibri', 11), width=12, justify='center', state='readonly')
        temp.grid(row=10, column=22, sticky='w', padx=0, pady=0, rowspan=1, columnspan=3)

        displaySplitStatus = tk.StringVar(value='  SPLIT NOT BALANCED')
        temp = tk.Entry(root, textvariable=displaySplitStatus, font=('Calibri', 11), width=72, justify='left', state='readonly')
        temp.grid(row=22, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=18)

        # Selection boxes
        selectionExpenses = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionExpenses, font=('Calibri', 11), width=80)
        temp.grid(row=16, column=5, sticky='w', rowspan=1, columnspan=20)
        temp['values'] = [m for m in range(1, 13)]

        selectionLiability = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionLiability, font=('Calibri', 11), width=80)
        temp.grid(row=18, column=5, sticky='w', rowspan=1, columnspan=20)
        temp['values'] = [m for m in range(1, 13)]

        selectionIncome = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionIncome, font=('Calibri', 11), width=80)
        temp.grid(row=20, column=5, sticky='w', rowspan=1, columnspan=20)
        temp['values'] = [m for m in range(1, 13)]

        selectionAsset = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionAsset, font=('Calibri', 11), width=80)
        temp.grid(row=22, column=5, sticky='w', rowspan=1, columnspan=20)
        temp['values'] = [m for m in range(1, 13)]

        selectionImport = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionImport, font=('Calibri', 11), width=60)
        temp.grid(row=2, column=28, sticky='w', rowspan=1, columnspan=14)
        temp['values'] = [m for m in range(1, 13)]

        selectionJournal = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionJournal, font=('Calibri', 11), width=60)
        temp.grid(row=4, column=28, sticky='w', rowspan=1, columnspan=14)
        temp['values'] = [m for m in range(1, 13)]

        selectionJournal = tk.StringVar()
        temp = ttk.Combobox(root, textvariable=selectionJournal, font=('Calibri', 11), width=72)
        temp.grid(row=10, column=31, sticky='w', rowspan=1, columnspan=18)
        temp['values'] = [m for m in range(1, 13)]

        # Input boxes
        inputMemo = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputMemo, font=('Calibri', 11), width=72, justify='left')
        temp.grid(row=12, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=18)

        inputAmount = tk.StringVar(value='')
        temp = tk.Entry(root, textvariable=inputAmount, font=('Calibri', 11), width=16, justify='left')
        temp.grid(row=15, column=31, sticky='w', padx=0, pady=0, rowspan=1, columnspan=4)

        # Preview box
        previewText = tk.StringVar(value='  Line:   Date:         Description:   ')
        temp = tk.Text(root, font=('Consolas', 9), width=170, height=15)
        temp.grid(row=27, column=13, sticky='w', padx=0, pady=0, rowspan=10, columnspan=36)
        temp.insert(tk.END, '  Line:   Date:         Description:   ')

        # Buttons
        temp = tk.Button(root, text='Start', font=('Calibri', 14, 'bold'))
        temp.grid(row=2, column=43, sticky='nesw', padx=20, pady=20, rowspan=3, columnspan=6)

        temp = tk.Button(root, text='Add Split', font=('Calibri', 14, 'bold'))
        temp.grid(row=18, column=32, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

        temp = tk.Button(root, text='Undo', font=('Calibri', 14, 'bold'))
        temp.grid(row=18, column=40, sticky='nesw', padx=20, pady=0, rowspan=2, columnspan=5)

        temp = tk.Button(root, text='Add to Ledger', font=('Calibri', 14, 'bold'))
        temp.grid(row=27, column=2, sticky='nesw', padx=20, pady=20, rowspan=6, columnspan=8)

        temp = tk.Button(root, text='Redo Last Entry', font=('Calibri', 14, 'bold'))
        temp.grid(row=34, column=3, sticky='nesw', padx=20, pady=20, rowspan=2, columnspan=6)


def Main():
     gui = MyGui()
     gui.root.mainloop()


Main()




# CUT


        # selectedImportFile = tk.StringVar()
        # temp = ttk.Combobox(root, textvariable=selectedImportFile)
        # temp.grid(row=2, column=2, sticky='nsew', rowspan=1, columnspan=5)
        # temp['values'] = [m for m in range(1, 13)]


        # # Setup resize event
        # self.root.bind('<Configure>', self.ResizeEvent)
        # self.curHeight = self.root.winfo_reqheight()
        # self.curWidth = self.root.winfo_reqwidth()


        # temp = tk.LabelFrame(root)
        # temp.grid(row=y, column=x, sticky='nesw', padx=0, pady=0, rowspan=1, columnspan=1)
        # for x in range(self.NUM_COLS):
        #     for y in range(self.NUM_ROWS):
        #         temp = tk.Label(root, text='x',  font=('Segoe UI', 9, 'bold'))
        #         temp.grid(row=x, column=y, sticky='nsew', padx=0, pady=0)

        # self.canvas = tk.Canvas(root, bg='green')
        # self.canvas.pack(fill=tk.BOTH, expand=True)
        # # self.canvas.grid(row=0, column=0, sticky='nesw', padx=0, pady=0, columnspan=self.NUM_COLS, rowspan=self.NUM_ROWS)

        # for x in range(self.NUM_COLS):
        #     for y in range(self.NUM_ROWS):
        #         self.canvas.create_line(x*self.COL_SIZE, 0, x*self.COL_SIZE, self.ROW_SIZE*self.NUM_ROWS, fill='#fff')
        #         self.canvas.create_line(0, y*self.ROW_SIZE, self.COL_SIZE*self.NUM_COLS, y*self.ROW_SIZE, fill='#fff')

        # self.canvas.addtag_all('all')

    # def ResizeEvent(self, event):
    #     ''' Resize of window occurred, adjust grid scaling '''
        # wscale = float(event.width)/self.curWidth
        # hscale = float(event.height)/self.curHeight
        # self.curWidth = event.width
        # self.curHeight = event.height
        # # # resize the canvas
        # # self.canvas.config(width=self.curWidth, height=self.curHeight)
        # # rescale all the objects tagged with the 'all' tag
        # self.canvas.scale('all',0,0,wscale,hscale)
        # print('balls')


'''
TKinter threading notes:

- Python threads are different than Tcl threads
    - Each Tcl thread has separate Tcl instance associated with it
        - Thread 1
            Tcl Interpreter 1
        - Thread 2
            Tcl Interpreter 2
    - Python interpreter can have many threads associated with it
        - Python
            - Thread 1
            - Thread 2


'''