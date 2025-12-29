import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

print("📥 Loading gtfs_labeled.csv...")
df = pd.read_csv("gtfs_labeled.csv")

df["is_peak"] = df["hour_of_day"].between(8, 11) | df["hour_of_day"].between(17, 20)
df["is_peak"] = df["is_peak"].astype(int)

features = [
    "hour_of_day",
    "distance_m",
    "is_peak"
]

X = df[features]
y = df["traffic_label"]

le = LabelEncoder()
y_enc = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

print("🌲 Training RandomForest...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
rf.fit(X_train, y_train)

print("📊 Evaluation:")
print(classification_report(y_test, rf.predict(X_test), target_names=le.classes_))

joblib.dump(rf, "traffic_rf_model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("✅ Model saved")
