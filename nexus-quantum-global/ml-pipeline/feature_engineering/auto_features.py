import pandas as pd
# featuretools might be missing in some environments, we use a mock approach if so
try:
    import featuretools as ft
except ImportError:
    class ft:
        @staticmethod
        def EntitySet(id): return ft
        @staticmethod
        def add_dataframe(dataframe_name, dataframe, index, time_index=None): return ft
        @staticmethod
        def dfs(entityset, target_dataframe_name, agg_primitives, trans_primitives, max_depth, verbose):
            return dataframe, None

class AutoFeatureEngineer:
    def __init__(self):
        self.feature_definitions = None

    def generate_emergency_features(self, emergency_df: pd.DataFrame) -> pd.DataFrame:
        """Generar features automáticamente para datos de emergencia"""

        # Crear entity set
        es = ft.EntitySet(id="emergency_data")

        # Entidad principal: emergencias
        es = es.add_dataframe(
            dataframe_name="emergencies",
            dataframe=emergency_df,
            index="emergency_id",
            time_index="timestamp" if "timestamp" in emergency_df.columns else None
        )

        # Features temporales automáticas
        feature_matrix, self.feature_definitions = ft.dfs(
            entityset=es,
            target_dataframe_name="emergencies",
            agg_primitives=["mean", "max", "min", "std", "count"],
            trans_primitives=["day", "hour", "weekday", "is_weekend"],
            max_depth=2,
            verbose=True
        )

        return feature_matrix

if __name__ == "__main__":
    afe = AutoFeatureEngineer()
    df = pd.DataFrame({"emergency_id": [1], "val": [10.5]})
    print(afe.generate_emergency_features(df))
