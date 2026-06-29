import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# -------- LOAD DATA --------
df = pd.read_csv("Data/AERO-BirdsEye-Data.csv")

# -------- CLEAN DATA --------
df = df.dropna()

# -------- TARGET VARIABLE --------
df['target'] = df['Status'].apply(lambda x: 1 if x == 'Completed' else 0)

# -------- FEATURES --------
X = df[['Enrollment', 'Start_Year']]
y = df['target']

# -------- TRAIN-TEST SPLIT --------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------- MODEL --------
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# -------- EVALUATION --------
y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print("\n✅ Model Evaluation:")
print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -------- SAVE MODEL --------
joblib.dump(model, "model.joblib")

print("\n✅ Model trained and saved as model.joblib")