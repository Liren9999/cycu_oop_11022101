import pandas as pd

# Load CSV data
df = pd.read_csv('20250520/midterm_scores.csv')

subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']

# Collect students failing 4 or more subjects
failing_students = []
for idx, row in df.iterrows():
    failed = [subj for subj in subjects if row[subj] < 60]
    if len(failed) >= 4:
        failing_students.append({
            'Name': row['Name'],
            'StudentID': row['StudentID'],
            'FailedSubjects': ', '.join(failed)
        })

# Save to CSV
failing_students_df = pd.DataFrame(failing_students)
failing_students_df.to_csv('20250520/failing_students.csv', index=False)

print("Students failing 4 or more subjects have been saved to '20250520/failing_students.csv'.")