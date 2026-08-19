from app.ml.trainer import train_model


class Dataset:
    def __init__(self, email_content, label):
        self.email_content = email_content
        self.label = label


dataset = [
    Dataset(
        "Congratulations you won $5000",
        "SPAM"
    ),
    Dataset(
        "You have won a free prize",
        "SPAM"
    ),
    Dataset(
        "Claim your free money now",
        "SPAM"
    ),
    Dataset(
        "Meeting at 10 AM tomorrow",
        "NOT_SPAM"
    ),
    Dataset(
        "Please review the project document",
        "NOT_SPAM"
    ),
    Dataset(
        "Can we schedule a meeting tomorrow",
        "NOT_SPAM"
    ),
    Dataset(
        "You won a free lottery prize",
        "SPAM"
    ),
    Dataset(
        "The project meeting is tomorrow",
        "NOT_SPAM"
    )
]


result = train_model(dataset)

print("Training completed")
print("Model:", result["model_name"])
print("Version:", result["model_version"])
print("Accuracy:", result["accuracy"])
print("Precision:", result["precision"])
print("Recall:", result["recall"])
print("F1:", result["f1_score"])
print("Confusion Matrix:")
print(result["confusion_matrix"])
print("Model:", result["model_path"])