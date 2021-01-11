from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import speech_recognition as sr
from gtts import gTTS 
import playsound
import sounddevice
import pyaudio
import pytz
import pyttsx3
import subprocess
import platform
import os
import random


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ['january' , 'febuary' , 'march' , 'april' , 'may' , 'june' , 'july' , 'august' , 'september' ,'october' ,'november' ,'december']
DAYS = ['monday' , 'tuesday' , 'wednesday' , 'thurseday' , 'friday' , 'saturday'  , 'sunday']
DAY_EXTENTIONS = ['rd' , 'th' ,'st' ,'nd']



#a function to  speak a text
def speak(text):
    tts = gTTS(text=text ,lang="en")
    file_name =  "voice.mp3"
    tts.save(file_name)
    playsound.playsound(file_name)
    os.remove(file_name)


# a function to Recognize speech to a text
def get_audio():
    r = sr.Recognizer()
    with  sr.Microphone() as source:
        r.adjust_for_ambient_noise(source , duration=1)
        print("Listening ....")
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
            
        except :
           print("Error :")
    return said.lower()



def authenticate_google():

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def get_event(day , service):
    #event start date
    date = datetime.datetime.combine( day, datetime.datetime.min.time())
    #event end date
    end = datetime.datetime.combine(day , datetime.datetime.max.time())
    utc = pytz.UTC
    date =  date.astimezone(utc)
    end = end.astimezone(utc)


    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(),timeMax=end.isoformat(),
                                         singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speak('No upcoming events found.')
    else:
        n = int(len(events))
        speak(f"there is {n} events , here is youre events ,")   
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])

            if int(start_time.split(":")[0]) < 12:
                start_time  = start_time + "AM"

            else:
                start_time =  str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
                start_time = start_time + "PM"

                speak(event["summary"]+" at "+ start_time)
        
        

#service = authenticate_google()

def get_date(text):
    text = text.lower()
    today = datetime.date.today()
  #  tommorow = datetime.timedelta(days=1)
    if text.count("today")>0:
        return today

    day = -1
    day_of_week = -1
    year = today.year
    month = -1

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word)+1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif  word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[0:found])
                    except:
                        pass
    # if the month that we got is equels with the current month 
    if month < today.month and  month != -1:
        year += 1

    #if we didnt get month but we get th day
    if month == -1 and day != -1:
        #if current day is bigger than the day got by user so it means next month
        if day < today.day:
            month = today.month + 1
        
        else:
            month = today.month
    #if we got only the day 
    if month  == -1 and day == -1 and day != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count("next")>=1:
                dif += 7

        return today + datetime.timedelta(dif)
    #if the user just say the number of date
    if day != -1:
        return datetime.date(month=month , day=day , year=year)
def open_program(path):
    subprocess.call([path])
    
def note(text):
    date =  datetime.datetime.now()
    file_name = str(date).replace(":" ,"-")+"_note.txt"
    with open("file_name" , "w") as f:
        f.write(text)
    os_name = platform.system()
    #if os is mac
    if os_name == "Darwin":
         subprocess.Popen(["textedit" ,"notes/"+file_name])
    elif os_name == "Linux":
         subprocess.Popen(["gedit" ,"notes/"+file_name])
    elif os_name == "Windows":
        subprocess.Popen(["notepad.exe" ,"notes/"+file_name])
serv = authenticate_google()
WAKE = "hey"
while True:
    
    text = get_audio()
    if text == WAKE:

        speak("Hi , What can i do for you ?")
        text = get_audio()
        


        print(f"You said : {text}")

        #the sentences for runing clender API
        CALENDAR_STR = ["what should i do" , "what do i have" , "do i have plans" , "do i have events" , "am i busy" , "whats me events" ,"read my events"]

        for phrase in CALENDAR_STR:
            if phrase in text:
                data = get_date(text)
                if data:
                    get_event(data,serv)
                else:
                    speak("sorry . please try again")


                
        NOTE_STR = ["make a note","create a note" ,"create a new note" ,"make a new note","type this" ,"type this note"]

        for phrase in NOTE_STR:
            if phrase in text:
                speak("What would like me to write down for you ?")
                write_down = get_audio()
                note(write_down)
                speak("I've  made a note for that")