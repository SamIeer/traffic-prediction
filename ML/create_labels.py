import pandas as pd

print("📥 Loading gtfs_cleaned.csv...")
df = pd.read_csv("gtfs_cleaned.csv")

# Avoid division by zero
df = df[df["travel_time_sec"] > 0]

df["delay_ratio"] = df["delay_sec"] / df["travel_time_sec"]

def label_traffic(r):
    if r < 0.15:
        return "Light"
    elif r < 0.35:
        return "Moderate"
    else:
        return "Heavy"

df["traffic_label"] = df["delay_ratio"].apply(label_traffic)

print("📊 Label distribution:")
print(df["traffic_label"].value_counts())

df.to_csv("gtfs_labeled.csv", index=False)
print("✅ gtfs_labeled.csv created (REALISTIC)")
