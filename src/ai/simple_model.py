class SimpleCentroidClassifier:
    def __init__(self):
        self.labels = []
        self.centroids = {}
        self.scales = []

    def fit(self, rows, labels):
        if not rows:
            raise ValueError("Training data is empty.")

        feature_count = len(rows[0])
        columns = list(zip(*rows))
        self.scales = [
            max(column) - min(column) or 1.0
            for column in columns
        ]

        self.labels = sorted(set(labels))
        for label in self.labels:
            members = [
                row for row, row_label in zip(rows, labels)
                if row_label == label
            ]
            if not members:
                continue

            centroid = [
                sum(row[index] for row in members) / len(members)
                for index in range(feature_count)
            ]
            self.centroids[label] = centroid

        return self

    def predict(self, rows):
        return [self._predict_one(row) for row in rows]

    def _predict_one(self, row):
        best_label = None
        best_distance = None

        for label, centroid in self.centroids.items():
            distance = sum(
                ((value - center) / scale) ** 2
                for value, center, scale in zip(row, centroid, self.scales)
            )
            if best_distance is None or distance < best_distance:
                best_label = label
                best_distance = distance

        if best_label is None:
            raise ValueError("Model has no trained labels.")
        return best_label
