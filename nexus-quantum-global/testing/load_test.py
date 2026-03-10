import asyncio
import aiohttp
import json
from datetime import datetime
import numpy as np

class EmergencySystemLoadTester:
    def __init__(self):
        self.base_url = "https://emergency-ai.example.com"
        self.concurrent_requests = 10
        self.test_duration = 30

    async def simulate_emergency_request(self, session, emergency_type):
        """Simular request de emergencia realista"""
        payload = {
            "emergency_type": emergency_type,
            "location": {
                "lat": float(np.random.uniform(-90, 90)),
                "lon": float(np.random.uniform(-180, 180))
            },
            "timestamp": datetime.now().isoformat(),
            "priority": str(np.random.choice(["low", "medium", "high", "critical"])),
            "description": f"Simulated {emergency_type} emergency",
            "sensor_data": {
                "temperature": float(np.random.uniform(-20, 50)),
                "humidity": float(np.random.uniform(0, 100)),
                "wind_speed": float(np.random.uniform(0, 50))
            }
        }

        try:
            # Note: This is a simulation, the URL might not exist
            async with session.post(f"{self.base_url}/api/v1/emergency",
                                  json=payload, timeout=2) as response:
                return {
                    "status": response.status,
                    "emergency_type": emergency_type
                }
        except Exception as e:
            return {"error": str(e), "emergency_type": emergency_type}

    async def run_load_test(self):
        """Ejecutar test de carga completo"""
        emergency_types = ["fire", "flood", "earthquake", "medical", "accident"]

        async with aiohttp.ClientSession() as session:
            tasks = []
            for _ in range(self.concurrent_requests):
                emergency_type = np.random.choice(emergency_types)
                task = self.simulate_emergency_request(session, emergency_type)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)
            self.analyze_results(results)

    def analyze_results(self, results):
        """Analizar resultados del load test"""
        successful = len([r for r in results if isinstance(r, dict) and r.get('status') == 200])
        failed = len([r for r in results if isinstance(r, dict) and r.get('error')])

        print(f"✅ Successful requests: {successful}")
        print(f"❌ Failed requests: {failed}")

if __name__ == "__main__":
    tester = EmergencySystemLoadTester()
    asyncio.run(tester.run_load_test())
