import gspread
import pickle

from datetime import datetime as dt

class msg_filter:
    def __init__(self):
        self.syntax = {
            'Reminder':(('date','time','note')),
            'Schedule':('days of week', 'time', 'note'),
            'Spent':(('Spent',), lambda x: self.money_spent(x)),
            'Transferred':(('Transferred', 'from', 'to',), lambda x: self.money_transfer(x)),
            'Invested':(),
            'Income':(),
            'MTI':((), lambda x : self.mti(x)),
            'Checking':((), lambda x : self.checking(x)),
            'Savings':(),
            'Roth':(),
            'Webull':(),
            'Total':()
        }
        self.spreadsheet_ref = {
            'Checking':'H5',
            'Savings':'I5',
            'Roth IRA':'J5',
            'Webull':'K5',
            'Total':'I8',
            'MTI':'H11'
        }
        self.spreadsheet_local = []
        
        with open('serial/sheets_index.p', 'wb') as f:
            pickle.dump(self.spreadsheet_ref, f)
        
        # used for pulling budget data from Google Sheets doc
        self.sa = gspread.service_account(filename='key.json')
        self.sheet = self.sa.open('Budget')
        
        # referenced when pulling budget data (2022 sheet)
        self.wks = self.sheet.worksheet('2022')
        
        self.spreadsheet_local = self.wks.get_all_values()
        
        # infile = open('serial/sheets_index.p','rb')
        # self.spreadsheet_data = pickle.load(infile)
        # infile.close()
        
    def filter_message(self, msg):
        parse = msg.split()   
        for key, value in self.syntax.items():
            if key == parse[0]:
                for i in parse:
                    for j in value[0]:
                        if i == j:
                            parse.remove(i)
                value[1](parse)
                break
            
    def money_transfer(self, msg):
        print(msg)
        print(dt.strptime(str(self.wks.acell('M5').value), "%m/%d/%y"))
        
    def money_spent(self, msg):
        print(self.wks.acell('M5').value)
        print(dt.strptime(str(self.wks.acell('M5').value), "%m/%d/%Y"))
        
    def mti(self, msg):
        print(self.wks.acell('H11').value)
        
    def checking(self, msg):
        print(msg)
        
        
    def email_conf(self,msg):
        pass