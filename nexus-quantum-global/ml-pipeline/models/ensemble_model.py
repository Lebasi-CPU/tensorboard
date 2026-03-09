import numpy as np
from typing import List, Dict

# Mocking tensorflow if not available
try:
    import tensorflow as tf
except ImportError:
    class tf:
        class keras:
            class models:
                @staticmethod
                def load_model(path): return tf.keras.models.Model()
                class Model:
                    def predict(self, data): return np.random.rand(data.shape[0], 5)

class EmergencyEnsembleModel:
    def __init__(self, model_paths: List[str]):
        self.models = []
        self.model_weights = []

        for path in model_paths:
            try:
                model = tf.keras.models.load_model(path)
                self.models.append(model)
            except Exception:
                # If path doesn't exist, we skip or use a mock
                pass

        # Pesos basados en performance histórica
        self.model_weights = self.calculate_model_weights()

    def calculate_model_weights(self) -> List[float]:
        """Calcular pesos de modelos basado en métricas históricas"""
        historical_performance = {
            'lstm_model': {'recall': 0.92, 'precision': 0.89},
            'transformer_model': {'recall': 0.94, 'precision': 0.87},
            'cnn_model': {'recall': 0.88, 'precision': 0.93}
        }

        weights = []
        # Match only existing models
        for i in range(len(self.models)):
            metrics = list(historical_performance.values())[i % len(historical_performance)]
            f1 = 2 * (metrics['recall'] * metrics['precision']) / (metrics['recall'] + metrics['precision'])
            weights.append(f1)

        # Normalizar pesos
        total_weight = sum(weights) if weights else 1.0
        return [w / total_weight for w in weights]

    def predict(self, input_data: np.ndarray) -> Dict:
        """Predicción con ensemble de modelos"""
        if not self.models:
            return {"error": "No models loaded"}

        predictions = []
        confidences = []

        for i, model in enumerate(self.models):
            pred = model.predict(input_data)
            predictions.append(pred)

            # Calcular confianza basada en entropía
            entropy = -np.sum(pred * np.log(pred + 1e-10), axis=1)
            confidence = 1 - (entropy / np.log(pred.shape[1]))
            confidences.append(confidence)

        # Weighted voting con confianza
        weighted_predictions = []
        for i, (pred, conf) in enumerate(zip(predictions, confidences)):
            weight = self.model_weights[i] * conf
            weighted_predictions.append(pred * weight.reshape(-1, 1))

        final_prediction = np.mean(weighted_predictions, axis=0)
        final_confidence = np.mean(confidences, axis=0)

        # Detectar casos de baja confianza (posible drift)
        low_confidence_threshold = 0.7
        drift_detected = np.any(final_confidence < low_confidence_threshold)

        return {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'drift_detected': drift_detected,
            'individual_predictions': predictions
        }
