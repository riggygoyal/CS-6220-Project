import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
import json

# Neural Network Model Setup
def create_model(shape):
  model = Sequential([
    Dense(128, activation='relu', input_shape=(shape[1],)),
    BatchNormalization(),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dense(1)  # Output layer for regression
  ])

  model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

  return model

# Pull labeled schedule data and preprocess
df = pd.read_csv('schedules-labeled.csv').drop([
    'Quality Score (Rigved)',
    'Quality Score (Brandon)',
    'Quality Score (Shayar',
    'Quality Score (g)',
    'Quality Score (Suraj',
    'Fitness function',
    'Earliest Time',
    'Latest Time',
], axis=1)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Remove Sections column
df = df.drop('Sections', axis=1)

df = df.astype(float)

# Split train/test data, Feature and Target Variables
X = df.drop('Quality Score', axis=1)
y = df['Quality Score']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

model = create_model(X_train.shape)

model.fit(X_train, y_train, epochs=50)

pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, pred))

print('RMSE: ' + str(rmse))

plt.plot(np.array(df.index[-len(y_test):]), np.array(y_test), label='Actual')
plt.plot(np.array(df.index[-len(y_test):]), pred, label='Predicted')
plt.xlabel('Schedules')
plt.ylabel('Quality Score')
plt.legend()