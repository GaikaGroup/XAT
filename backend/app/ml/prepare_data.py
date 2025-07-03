import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load the tokenized dataset
df = pd.read_csv('tokenized_proverbs.csv')

# Check the first few rows to ensure it's loaded correctly
print(df.head())

# Prepare features (input) and labels (output)
X = df['encoded'].tolist()  # Tokenized proverbs
y = df['Sentiment']  # Sentiment labels

# Encode labels (Positive, Negative, Neutral -> 0, 1, 2)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the data into training and test sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Display the size of the splits
print(f"Training data size: {len(X_train)}")
print(f"Test data size: {len(X_test)}")
