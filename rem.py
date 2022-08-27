import calendar
import gc
import imaplib, email
import base64

import os.path
import time

import json

import threading

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

import gspread
from datetime import date, datetime

from filter import msg_filter   

class Rem:
    def __init__(self):
        
        # Email being scanned for messages
        self.user = "griffins.virtual.assistant@gmail.com"
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # ensures earlier messages aren't filtered
        self.prev_scan = str(calendar.timegm(time.gmtime()))
        self.prev_token_time = 0
        
        # GMAIL service and credits needed for OAuth2 verification
        self.gmail_service = None
        self.creds = None
        
        self.message_filter = msg_filter()
                     
    def authenticate(self):
        
        # GMAIL/SHEETS API Authentication 
        # Two Google API services are created - GMAIL & SHEETS
    
        # This block of code is from Google's quickstart guide - used to obtain OAuth2 tokens using credentials.json
        self.creds = None
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        # Stores the time of OAuth2 token instantiation - must be refreshed before expiring in one hour per google api rules
        self.prev_token_time = calendar.timegm(time.gmtime())
        
        # Call the Gmail API - Services used in search_messages()
        try:
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            print(error)
      
    def refresh_token(self):
        
        # essentially a lighter version of the authentication() method
        if not os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
        self.creds.refresh(Request())
        with open('token.json', 'w') as token:
            token.write(self.creds.to_json())
            
        self.prev_token_time = calendar.timegm(time.gmtime())
        
        try:
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        except HttpError as error:
            print(error)
             
    def search_messages(self):
        
        print(calendar.timegm(time.gmtime()) - self.prev_token_time)
        
        # Refreshes the OAuth token every 50 minutes
        if calendar.timegm(time.gmtime()) - self.prev_token_time > 3000:
            self.refresh_token()
            print('token refreshed')
        
        try:
            result = self.gmail_service.users().messages().list(
                userId='me', labelIds=['INBOX'], q='from:12104170588@tmomail.net after:' + self.prev_scan, maxResults=20
                ).execute()
            messages = result.get('messages', [])
            
            if messages:
                self.prev_scan = str(calendar.timegm(time.gmtime()))
            
                for message in messages:
                    msg = self.gmail_service.users().messages().get(userId='me', id=message['id']).execute()
                    print(msg['snippet'])
                    
                    threading.Thread(target=self.message_filter.filter_message, args=(msg['snippet'],)).start()
            
        except HttpError as error:
            print(f'An error occurred: {error}')