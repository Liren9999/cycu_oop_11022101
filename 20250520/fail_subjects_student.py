import pandas as pd

# Load CSV data
df = pd.read_csv('20250520/midterm_scores.csv')

subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']

print("Students failing 4 or more subjects:")
for idx, row in df.iterrows():
    failed = [subj for subj in subjects if row[subj] < 60]
    if len(failed) >= 4:
        print(f"{row['Name']} (ID: {row['StudentID']}), Failed subjects: {', '.join(failed)}")