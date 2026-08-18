import pandas as pd

df = pd.read_csv("dataset/raw/d2_sms_smishing_raw.csv")

d2 = df[["text", "labels"]].rename(columns={"labels": "label"})
d2["label"] = d2["label"].map({"ham": 0, "spam": 1})

d2.to_csv("dataset/raw/d2_sms_smishing.csv", index=False)
print(f"Saved {len(d2)} rows")
print(d2["label"].value_counts())