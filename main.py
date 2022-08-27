from rem import Rem
import time
import apscheduler.schedulers.blocking
import apscheduler.schedulers.background
  
if __name__ == '__main__':
    
    schedule = Rem()
    schedule.authenticate()
    
    scheduler = apscheduler.schedulers.background.BlockingScheduler(daemon=True)
    
    # checks for user input through SMS
    scheduler.add_job(lambda : schedule.search_messages(),'interval', seconds=3)
    scheduler.start()