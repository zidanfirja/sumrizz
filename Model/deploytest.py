import tensorflow as tf
from tensorflow.keras import callbacks, models, layers, preprocessing as kprocessing #(2.6.0)
import pandas as pd
import json
from nltk.corpus import stopwords
import regex as re
import numpy as np

def run_model(sample):
    # Open tokenizer for text
    with open('word_corpus.json') as f: 
            data = json.load(f) 
            text_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(data)

    # Open tokenizer for summary
    with open('label_corpus.json') as f: 
            data = json.load(f) 
            label_tokenizer = tf.keras.preprocessing.text.tokenizer_from_json(data)

    # Define special tokens for summary
    special_tokens = ("xstartx", "xendx")

    # Load encoder and decoder models
    encoder_model = tf.keras.models.load_model('encoder_191223.h5')
    decoder_model = tf.keras.models.load_model('decoder_191223.h5')

    # Text input

    # Data cleansing
    clean_sample = re.sub("[-()\"#/@;:<>{}`+=~|.!?,]", "", sample.lower())

    # Define stopwords
    stopword = stopwords.words("english")

    temp=""
    text=clean_sample.split(" ")
    for word in text:
        if word not in stopword:
            temp = temp+" "+word
    clean_sample = temp
    input_sample = []
    input_sample.append(clean_sample.strip())

    input_seq = text_tokenizer.texts_to_sequences(input_sample)

    # Padding sequence
    x = tf.keras.utils.pad_sequences(input_seq, maxlen=800, padding='post', truncating="post")

    # Predict Manual
    x = x.reshape(1, -1)

    # encode X
    encoder_out, state_h, state_c = encoder_model.predict(x, verbose=0)

    # prepare loop
    y_inp = np.array([label_tokenizer.word_index[special_tokens[1]]])
    y_expand = np.expand_dims(y_inp, axis=1)
    predicted_text = ""
    stop = False

    while not stop:
        # predict dictionary probability distribution
        outputs = decoder_model.predict([y_expand, state_h, state_c], verbose=0)
        probs, new_state_h, new_state_c = outputs[0], outputs[1], outputs[2]

        # get predicted word
        voc_idx = np.argmax(probs[0, -1, :], axis=0)
        if voc_idx == 0:
            break

        pred_word = label_tokenizer.index_word[voc_idx]

        # check stop
        if (pred_word != special_tokens[1]) and (len(predicted_text.split()) < 50):
            predicted_text = predicted_text + " " + pred_word
        else:
            stop = True

        # next
        y_inp = np.array([voc_idx])
        y_expand = np.expand_dims(y_inp, axis=1)
        state_h, state_c = new_state_h, new_state_c


    return predicted_text
    '''
        Summary will be stored in the 'predicted_text' variable.
    '''


# result = run_model('belajar behasa pemrograman')
# print(result)