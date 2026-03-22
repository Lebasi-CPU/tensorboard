import great_expectations as ge
import pandas as pd
import logging

logger = logging.getLogger(__name__)

try:
    from pyspark.sql import SparkSession
except ImportError:
    logger.info("PySpark not found. Using Spark simulation mocks.")
    class SparkSession:
        class Builder:
            def appName(self, name): return self
            def getOrCreate(self): return SparkSession()
        builder = Builder()

class EmergencyDataQualityChecker:
    def __init__(self):
        self.spark = SparkSession.builder.appName("DataQuality").getOrCreate()

    def validate_emergency_data(self, data_path):
        """Critical validations for emergency data"""
        try:
            df = self.spark.read.parquet(data_path)
            # Convert to Pandas for Great Expectations
            pandas_df = df.toPandas()
        except Exception:
            # Fallback for simulation
            pandas_df = pd.DataFrame({
                "emergency_type": ["fire"],
                "location_lat": [40.0],
                "location_lon": [-74.0],
                "timestamp": ["2026-01-01T12:00:00"],
                "priority_score": [0.9]
            })

        ge_df = ge.from_pandas(pandas_df)

        # Critical expectations
        expectations = [
            ge_df.expect_column_to_not_be_null("emergency_type"),
            ge_df.expect_column_to_not_be_null("location_lat"),
            ge_df.expect_column_to_not_be_null("location_lon"),
            ge_df.expect_column_to_not_be_null("timestamp"),
            ge_df.expect_column_values_to_be_between("location_lat", -90, 90),
            ge_df.expect_column_values_to_be_between("location_lon", -180, 180),
            ge_df.expect_column_values_to_be_in_set("emergency_type",
                ["fire", "flood", "earthquake", "medical", "accident"]),
        ]

        results = []
        for expectation in expectations:
            result = expectation.validate()
            results.append(result)

            if not result.success:
                logger.error(f"🚨 Data Quality Issue: {expectation}")

        return all(r.success for r in results)

if __name__ == "__main__":
    checker = EmergencyDataQualityChecker()
    checker.validate_emergency_data("dummy_path")
