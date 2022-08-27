def authenticate(self):
        
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        self.service = service
        
    def search_messages(self):
        
        try:
            result = self.service.users().messages().list(
                userId='me', labelIds=['INBOX'], q='from:12104170588@tmomail.net after:' + self.prev_scan, maxResults=20
                ).execute()
            messages = result.get('messages', [])
            
            if messages:
                self.prev_scan = str(calendar.timegm(time.gmtime()))
            
            for message in messages:

                msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
                #print(msg['snippet'])
                #self.scan_message(msg['snippet'])
                self.scan_message(msg['snippet'])
                
        except HttpError as error:
            print(f'An error occurred: {error}')
            
        print('scanned at:' + str(calendar.timegm(time.gmtime())))