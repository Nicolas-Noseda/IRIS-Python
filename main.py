import io
import os
import time

import boto3
import openai
import pygame.mixer
import speech_recognition as sr

openai.api_key = os.environ.get("OPENAI_API_KEY")
session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_ACCESS_KEY_SECRET"),
    region_name=os.environ.get("AWS_REGION_NAME")
)
recognizer = sr.Recognizer()
polly = session.client('polly')


def iris_say(text):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId="Lea"
        # ID de la voix, par exemple "Joanna" pour voix anglaise
    )
    pygame.mixer.init()
    pygame.mixer.music.load(io.BytesIO(response['AudioStream'].read()))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def listen_microphone():
    with sr.Microphone() as source:
        audio = recognizer.listen(source, timeout=15)
    try:
        return recognizer.recognize_google(audio, language='fr-FR')
    except sr.WaitTimeoutError:
        print('timeout')
        listen_microphone()
    except sr.UnknownValueError:
        print('erreur inconnu')
    except sr.RequestError as e:
        iris_say("Une erreur s'est produite lors de la demande au service Google : {0}".format(e))


def ask_chat_gpt(text):
    response_chat_gpt = openai.Completion.create(
        engine="text-davinci-003",
        prompt=text,
        max_tokens=100,
        temperature=0.8
    )
    return response_chat_gpt.choices[0].text.strip()


def main():
    while True:
        text = listen_microphone()
        print(text)
        if text is not None:
            if 'iris' in text.lower():
                iris_say('Bonjour, que puis-je faire pour vous ?')
                text = listen_microphone()
                print(text)
            text_response = ask_chat_gpt(text)
            print(text_response)
            iris_say(text_response)
            time.sleep(2)


if __name__ == "__main__":
    main()
