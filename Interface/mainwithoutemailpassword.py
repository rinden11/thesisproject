# -*- coding: utf-8 -*-

import streamlit as st
import pickle
import string
from nltk.corpus import stopwords
import nltk
from nltk.stem.porter import PorterStemmer
import smtplib
from langdetect import detect
from googletrans import Translator

smtp_server = "smtp.mail.yahoo.com"
smtp_port = 465
username = "***@yahoo.com"
password = "***"
from_address = "emailappnotification@yahoo.com"
to_address = "***@yahoo.com"

ps = PorterStemmer()


def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)


tfidf = pickle.load(open('vectorizer.pkl', 'rb'))
model = pickle.load(open('model.pkl', 'rb'))

st.title("Email Spam Classifier")

input_sms = st.text_area("Introduceți Email-ul:")

input_spam_subject = "Acest email este spam!"
input_spam_text = "Emailul a fost detectat ca și spam și conține elemente dăunătoare, vă rugăm să îl ștergeți!"
input_nospam_subject = "Acest email nu este spam."
input_nospam_text = "Nu au fost detectate elemente dăunătoare în cadrul acestui email."

if st.button('Predicție:'):
    # 1. Preprocesare
    transformed_sms = transform_text(input_sms)
    # 2. Vectorizare
    vector_input = tfidf.transform([transformed_sms])
    # 3. Prezice
    result = model.predict(vector_input)[0]

    detected_language = detect(transformed_sms)
    text = str(result)

    if detected_language != 'en':
        st.write(f"Text detectat: {detected_language}")
        translator = Translator()
        try:
            translation = translator.translate(transformed_sms, src=detected_language, dest='en')
            if translation is not None and translation.text is not None:
                st.write(f"Text tradus: {translation.text}")
            else:
                st.write("Traducere eșuată.")
        except Exception as e:
            st.write(f"S-a produs o eroare în timpul traducerii: {str(e)}")
    else:
        translator = Translator()
        try:
            translation = translator.translate(transformed_sms, src=detected_language, dest='en')
            if translation is not None and translation.text is not None:
                st.write(translation.text)
            else:
                st.write("Traducere eșuată.")
        except Exception as e:
            st.write(f"S-a produs o eroare în timpul traducerii: {str(e)}")

    # 4. Display
    if result == 1:
        st.header("Spam!")
        sender_email = username
        sender_password = password
        recipient_email = to_address
        message = 'Subject: {}\n\n{}'.format(input_spam_subject, input_spam_text)
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, recipient_email, message.encode('utf-8'))
    else:
        st.header("Nu e Spam.")
        sender_email = username
        sender_password = password
        recipient_email = to_address
        message = 'Subject: {}\n\n{}'.format(input_nospam_subject, input_nospam_text)
        with smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.sendmail(sender_email, recipient_email, message.encode('utf-8'))