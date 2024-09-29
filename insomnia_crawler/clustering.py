from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Sample text data
texts = [
    "σύμφωνα με τη σελίδα στα Mutirama ΛΙΣΤΑ ΤΗΛΕΟΡΑΣΕΩΝ LCD ΚΑΙ PLASMA...",
    "Sony Bravia KDL-40D3400, KDL-46D3400, KDL-40D3500...",
    "Samsung LE32A456C2DXXC, LE46A566P1XZF, LE46A676A1MXZF...",
    # Add more text samples here
]

# Step 1: Vectorization at the character level
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 4), max_features=1000)
X = vectorizer.fit_transform(texts)

# Step 2: Dimensionality reduction (optional but recommended for visualization)
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X.toarray())

# Step 3: Clustering
num_clusters = 3  # Adjust based on your needs
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(X_reduced)
labels = kmeans.labels_

# Step 4: Visualization (optional)
plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=labels, cmap='viridis')
plt.title('Character-Level Clustering of Texts')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.show()

# Display cluster assignments
for i, label in enumerate(labels):
    print(f"Text {i} is in cluster {label}")
