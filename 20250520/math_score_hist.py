import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv('20250520/midterm_scores.csv')

# Subjects
subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']

# Define bins: 0-9, 10-19, ..., 90-100
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
bin_labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]

# Colors for each subject (rainbow colors)
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'purple']

# Create a histogram for all subjects
bar_width = 0.1  # Width of each bar
x = np.arange(len(bin_labels))  # X positions for bins

plt.figure(figsize=(12, 8))

for i, subject in enumerate(subjects):
    # Calculate histogram for the current subject
    counts, _ = np.histogram(df[subject], bins=bins)
    # Offset each subject's bars to avoid overlap
    plt.bar(x + i * bar_width, counts, width=bar_width, label=subject, color=colors[i])

# Add labels, title, and legend
plt.xlabel('Score Range')
plt.ylabel('Number of Students')
plt.title('Score Distribution Across All Subjects')
plt.xticks(x + (len(subjects) - 1) * bar_width / 2, bin_labels, rotation=45)
plt.legend(title="Subjects")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Show the plot
plt.show()