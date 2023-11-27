import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam

# Preprocessing and Sample Data here

# Will be replaced by generated schedules?
sample_data = {
    'average_gpa': np.random.uniform(2.0, 4.0, 100),
    'total_time_gap': np.random.randint(0, 180, 100),  # in minutes
    # assuming 8am to 12pm start times
    'start_time': np.random.randint(8, 12, 100),
    # assuming 2pm to 8pm end times
    'end_time': np.random.randint(14, 20, 100),
    # hypothetical quality score
    'quality_score': np.random.uniform(0, 10, 100)
}

# Create DataFrame
df = pd.DataFrame(sample_data)

# Feature and Target Variables
X = df.drop('quality_score', axis=1)
y = df['quality_score']

# Split Data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Standardize Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Neural Network Model Setup
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    BatchNormalization(),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dense(1)  # Output layer for regression
])

# Model Compilation
model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
