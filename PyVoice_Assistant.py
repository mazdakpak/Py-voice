import os
import time
import speech_recognition as sr
from gtts import gTTS
import playsound
import sounddevice
import pyaudio


#a function to  speak a text
def speak(text):
    tts = gTTS(text=text ,lang="en")
    file_name =  "voice.mp3"
    tts.save(file_name)
    playsound.playsound(file_name)
    os.remove(file_name)


def get_audio():
    r = sr.Recognizer()
    with  sr.Microphone() as source:
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as ex:
            print("Error :"+str(ex))
    return said
get_audio()