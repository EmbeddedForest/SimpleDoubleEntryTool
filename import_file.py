#------------------------------------------------------------------------------
# File:
#   import_file.py
#
# Author:
#   EmbeddedForest
#
# Date:
#   01/17/2026
#
# Description:
#   This file creates a class which manages transaction data to be imported.
#
#------------------------------------------------------------------------------

import os
import csv
import yaml
import hashlib
import pandas as pd
import constants as c
from decimal import Decimal, ROUND_HALF_UP


class ImportFile():
    ''' Class which manages the transaction data to be imported '''

    dateData = []
    descData = []
    amntData = []
    hashData = []
    assAccts = []
    numTrans = 0
    importIndex = 0
    active = False
    importFileList = []

    def __init__(self):
        self._LoadDataFileNames()

    def Setup(self, filePath):
        ''' Set up specified transaction import file '''
        self._ResetData()

        #----------------------------------------------------------------------
        # Make sure config is present
        #----------------------------------------------------------------------
        try:
            with open(c.CONFIG_FILE) as f:
                config = yaml.safe_load(f)

        except FileNotFoundError:
            log = 'Config file does not exist', 'error'
            return c.BAD, log

        #----------------------------------------------------------------------
        # Make sure import file exists
        #----------------------------------------------------------------------
        try:
            with open(filePath, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                cols = list(next(reader).keys())

        except FileNotFoundError:
            log = 'Selected Import csv file does not exist', 'error'
            return c.BAD, log

        except PermissionError:
            log = 'Selected import csv needs to be closed', 'error'
            return c.BAD, log

        #----------------------------------------------------------------------
        # Determine import file style
        #----------------------------------------------------------------------
        style = ''
        for styleName, styleCfg in config['ImportFileStyles'].items():
            dateC = styleCfg.get('DateColName')
            descC = styleCfg.get('DescColName')
            amntC = styleCfg.get('AmntColName')
            amntNeg = styleCfg.get('AmntNegate')
            assAccts = styleCfg.get('AssAccts')
            skipList = styleCfg.get('SkipStrings')

            if (dateC in cols) and (descC in cols) and (amntC in cols):
                style = styleName
                break

        if (style == ''):
            log = 'Import file does not match any known styles', 'error'
            return c.BAD, log

        #----------------------------------------------------------------------
        # Negate amount if style says to
        #----------------------------------------------------------------------
        tmpAmnts = []
        df = pd.read_csv(filePath, index_col=False)

        if (amntNeg == True):
            for value in df[amntC]:
                newVal = -1 * value
                tmpAmnts.append(newVal)

            df[amntC] = tmpAmnts

        #----------------------------------------------------------------------
        # Remove any transactions whose description matches any SkipStrings
        #----------------------------------------------------------------------
        for desc in skipList:
            df = df[~df[descC].str.contains(desc, na=False, case=False)]

        #----------------------------------------------------------------------
        # Normalize data
        #----------------------------------------------------------------------
        # Date data (yyyy-mm-dd)
        df[dateC] =pd.to_datetime(df[dateC], format='mixed', dayfirst=False)
        df[dateC] = df[dateC].dt.strftime('%Y-%m-%d')

        # Amount data (decimal to 2 places then convert to string)
        tmpAmnts = []
        for value in df[amntC]:
            dec = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            tmpAmnts.append(dec)

        df[amntC] = tmpAmnts
        df[amntC] = df[amntC].astype(str)

        # Description data (only take first 50 characters)
        df[descC] = df[descC].str.strip().str[:50]

        # Order by date and description
        df = df.sort_values(by=[dateC, descC])

        #----------------------------------------------------------------------
        # Create temporary file to hold new df
        #----------------------------------------------------------------------
        try:
            df.to_csv(c.TEMP_FILE, index=False)

        except PermissionError:
            log = 'ImportTemp.csv needs to be closed', 'error'
            return c.BAD, log

        #----------------------------------------------------------------------
        # Give each transaction unique hash
        #----------------------------------------------------------------------
        count = 0
        prevId = ''
        hashes = []

        for index, row in df.iterrows():
            date = row[dateC]
            desc = row[descC]
            amnt = row[amntC]

            stringToHash = str(date) + desc + str(amnt) + str(count)
            encodedString = stringToHash.encode('utf-8')
            fullHash = hashlib.md5(encodedString).hexdigest()

            if (fullHash == prevId):
                # This accounts for multiple identical transactions in a row
                count = count + 1
                stringToHash = str(date) + desc + str(amnt) + str(count)
                encodedString = stringToHash.encode('utf-8')
                fullHash = hashlib.md5(encodedString).hexdigest()
            else:
                count = 0
                stringToHash = str(date) + desc + str(amnt) + str(count)
                encodedString = stringToHash.encode('utf-8')
                fullHash = hashlib.md5(encodedString).hexdigest()

            hashes.append(fullHash)
            prevId = fullHash

        # Insert hashes into temp file
        df['TransactionID'] = hashes
        df.to_csv(c.TEMP_FILE, index=False)

        #----------------------------------------------------------------------
        # Update object data
        #----------------------------------------------------------------------
        self.dateData = df[dateC].tolist()
        self.descData = df[descC].tolist()
        self.amntData = df[amntC].tolist()
        self.hashData = df['TransactionID'].tolist()
        self.numTrans = len(df)
        self.active = True
        self.assAccts = assAccts

        log = 'Import setup is complete', 'default'
        return c.GOOD, log

    def _ResetData(self):
        ''' Note - not resetting csv file name list, that stays const '''
        self.dateData = []
        self.descData = []
        self.amntData = []
        self.hashData = []
        self.assAccts = []
        self.numTrans = 0
        self.importIndex = 0
        self.active = False

    def _LoadDataFileNames(self):
        ''' Load all csv file names from Data folder into list '''
        self.importFileList = []

        for file in os.listdir(c.DATA_FOLDER):
            if (file.lower().endswith(".csv")):
                self.importFileList.append(file)