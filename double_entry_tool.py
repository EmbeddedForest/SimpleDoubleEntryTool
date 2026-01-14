import gui as g



'''
Brain Dump:

Should be all event driven.
    - only thing that should happen on startup is loading combo boxes during startup

- nothing can happen until the start button is pressed
- if any button is pressed before, show err msg in preview box
- start button pressed
    - check if import file valid
        - if not, show error msg in preview box
        - if valid, move to next
            - check that file name exists as csv
            - check that file has valid column headers
                - during this process we should be able to infer proper mapping
                    - date, description, amount
                    - also assumes which account it is for?
                        - ALT - add drop down in setup for account associated with import file
                        - ALT - it can assume but it also gives you ability to override, just like suggested account below
    - check if journal file valid
        - check if it has proper columns for ledger tab
        - check if it has proper columns for accounts tab
        - load accounts into proper combo boxes from accounts tab
    - find last entry in journal
    - iterate through transaction list one by one
        - check if transaction already exists in journal
            - something that could make this easier is ordering ledger by date first
                - ie: inject data into ledger rather than always at end?
                    - adds complexity and more opportunities for error, tougher to debug / see when something goes wrong
                    - also could accidentally "break" history, which is scary
                    - seems that most real life accounting ledgers order transactions chronologically, so injection is the move
            - how to handle identical transactions in same day?
                - TBD - but could do a count in transaction list of transactions of same description on same day with same amount
                    - if it is greater than 1, add a star or something
                    - maybe make temp local copy of transaction list and create a hash with all of the transaction data
                        - if I include hash for line number ?
                            - won't help with searching ledger though
                    - assuming transactions are always ordered by day in ascending order, can just add a check:
                        - if ledger says it alread exists, before saying sure and going to next, check if previous transaction had same date/amount/description
                            - if it did, add it to ledger as new entry
        - if it does, move to next transaction in list
        - during this process, find last transaction with same description - save account as suggested
    - present date, description, and amount
    - auto populate suggested account
        - update note in accounts box to say "auto suggested = TRUE" or similar
    - update preview window to show what double entry in ledger would look like with given inputs


Functions:
- error reporting with error message descriptions
- update import and journal combo boxes
    - read file names from current folder and folder called "data"
    - only include csv files to choose from
    - potentially add "date modified" information into dropdown description too so you know which is newest import
- import file check
- journal file check
- determine account associated with import file
    - update assumed account in GUI
- check if exists
    - check if multiple
- generate hash for transaction in ledger
- determine injection point (where to place transaction into ledge)
- generate preview of ledger entry
- present transaction data to GUI
- find last ledger entry for current transaction to assume new account
- populate GUI with assume account
    - combo boxes and note
- check if split is balanced
- update split status and preview


GUI updates so far:
- add new drop down in settings section to verify account associated with transaction list
- use preview window to present errors / instructions ?

'''


# def Setup():






def Main():
    gui = g.MyGui()

    # Bind buttons

    # Setup()

    gui.root.mainloop()


Main()