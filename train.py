import librosa
import numpy as np
import keras
from keras import backend as K
from keras import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import glob
from os.path import dirname, basename, join
from os import listdir
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import matplotlib.pyplot as plt
from multiprocessing import Pool
import joblib
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
from evaluation import evaluation

K.tensorflow_backend._get_available_gpus()


class CategoryEncoder:
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.one_hot_encoder = OneHotEncoder()

    def fit_transform(self, y):
        tmp = y
        tmp = self.label_encoder.fit_transform(tmp)
        tmp = tmp.reshape(len(tmp), 1)
        tmp = self.one_hot_encoder.fit_transform(tmp)
        return tmp

    def reverse_transform(self, y):
        return


train_data = joblib.load("tmp/train_full.data.bin")
test_data = joblib.load("tmp/test.data.bin")

labels = []
is_first = True
m = len(train_data)
for i, data in enumerate(train_data):
    label, features = data
    if i % 1000 == 0:
        print(f"{i}/{m}")
    n = features.shape[0]
    labels.extend(n * [label])
a, b = zip(*train_data)
X = np.concatenate(b)

encoder = CategoryEncoder()
y = encoder.fit_transform(labels)

input_shape = X.shape[1:]
num_classes = 6
batch_size = 32
epochs = 10

model = Sequential()
model.add(Conv2D(64, kernel_size=(7, 7), strides=(1, 1), activation='relu', input_shape=input_shape, padding='same'))
model.add(MaxPooling2D(pool_size=(3, 3), strides=(2, 2), padding='same'))
# model.add(Dropout(0.2))
model.add(Conv2D(128, kernel_size=(5, 5), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(256, kernel_size=(2, 2), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(200, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adam(lr=0.0001, beta_1=0.9, beta_2=0.999),
              metrics=['accuracy'])

model.summary()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
early_stopping = EarlyStopping(monitor='val_loss', patience=10)
history = model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1,
                    validation_data=(X_test, y_test),
                    callbacks=[early_stopping])

model.save('model.h5')


# evaluation("submission.csv", "data/public_test_gt.csv")

# Plot
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')
plt.show()
