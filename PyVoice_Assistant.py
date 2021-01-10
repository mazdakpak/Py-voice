import os
import time
import speech_recognition as sr
from gtts import gTTS
import playsound

def speak(text):
    tts = gTTS(text=text ,lang="en")
    file_name =  "voice.mp3"
    tts.save(file_name)
    playsound.playsound(file_name)
    os.remove(file_name)

