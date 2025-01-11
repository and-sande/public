import pandas as pd
import numpy as np

np.random.seed(42)
num_students = 100

#features
attendance = np.random.randint(50, 100, num_students)  # Attendance percentage
assignment_scores = np.random.randint(0, 100, num_students)  # Assignment scores
midterm_scores = np.random.randint(0, 100, num_students)  # Midterm scores

# Target (Pass/Fail: 1 for Pass, 0 for Fail)
# Let's assume passing requires:
# - Attendance >= 70%
# - Assignment scores >= 50
# - Midterm scores >= 50
pass_fail = np.where(
    (attendance >= 70) & (assignment_scores >= 50) & (midterm_scores >= 50),
    1,  # Pass
    0   # Fail
)

# Create a DataFrame
data = pd.DataFrame({
    'Attendance': attendance,
    'Assignment_Scores': assignment_scores,
    'Midterm_Scores': midterm_scores,
    'Pass_Fail': pass_fail
})

# Display the first 5 rows
print(data.head())
# Check basic statistics
print(data.describe())

# Check the distribution of the target variable (Pass/Fail)
print(data['Pass_Fail'].value_counts())

from sklearn.model_selection import train_test_split

# Features (X) and target (y)
X = data[['Attendance', 'Assignment_Scores', 'Midterm_Scores']]
y = data['Pass_Fail']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training set size:", X_train.shape)
print("Testing set size:", X_test.shape)

from sklearn.linear_model import LogisticRegression

# Create a Logistic Regression model
model = LogisticRegression()

# Train the model on the training data
model.fit(X_train, y_train)

# Predict the target for the test set
y_pred = model.predict(X_test)

# Display the predictions
print("Predicted labels:", y_pred)

from sklearn.metrics import accuracy_score, confusion_matrix

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)

# Create a confusion matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:\n", cm)

import seaborn as sns
import matplotlib.pyplot as plt

# Plot the confusion matrix
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Fail", "Pass"], yticklabels=["Fail", "Pass"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

import joblib

# Save the model to a file
joblib.dump(model, 'student_performance_model.pkl')

print("Model saved as 'student_performance_model.pkl'")