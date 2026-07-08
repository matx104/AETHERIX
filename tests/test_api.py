"""
Tests for AETHERIX Backend API (FastAPI).

Integration tests covering all 7 routers: health, simulations,
link-budget, routing, orbital, security, cmd.
Uses Starlette TestClient with an in-memory SQLite database.
"""

import os
import sys
import unittest

# Add both src and backend to path
_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_HERE, "..", "src")
_BACKEND = os.path.join(_HERE, "..", "backend")
for p in (_SRC, _BACKEND):
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Override the database with in-memory SQLite for testing
_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)
Base.metadata.create_all(bind=_test_engine)


def _override_get_db():
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db

client = TestClient(app)


class TestHealthRouter(unittest.TestCase):

    def test_health_check(self):
        resp = client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn(data["status"], ("ok", "healthy"))
        self.assertIn("version", data)
        self.assertIn("database", data)


class TestSimulationsRouter(unittest.TestCase):

    def test_list_simulations_empty(self):
        resp = client.get("/api/simulations/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_create_simulation(self):
        resp = client.post("/api/simulations/", json={
            "name": "test-run",
            "scenario": "earth-mars-baseline",
            "config": {"duration_hours": 24},
            "seed": 42,
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["name"], "test-run")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["seed"], 42)

    def test_get_simulation(self):
        create_resp = client.post("/api/simulations/", json={
            "name": "get-test",
            "scenario": "test-scenario",
        })
        sim_id = create_resp.json()["id"]
        resp = client.get(f"/api/simulations/{sim_id}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["name"], "get-test")

    def test_get_simulation_not_found(self):
        resp = client.get("/api/simulations/nonexistent-id")
        self.assertEqual(resp.status_code, 404)

    def test_delete_simulation(self):
        create_resp = client.post("/api/simulations/", json={
            "name": "delete-test",
            "scenario": "test",
        })
        sim_id = create_resp.json()["id"]
        resp = client.delete(f"/api/simulations/{sim_id}")
        self.assertEqual(resp.status_code, 204)

    def test_delete_simulation_not_found(self):
        resp = client.delete("/api/simulations/nonexistent-id")
        self.assertEqual(resp.status_code, 404)


class TestLinkBudgetRouter(unittest.TestCase):

    def test_optical_link_average(self):
        resp = client.post("/api/link-budget/optical", json={
            "scenario": "average",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["link_type"], "optical")
        self.assertIn("free_space_loss_db", data)
        self.assertIn("link_margin_db", data)

    def test_optical_link_custom_distance(self):
        resp = client.post("/api/link-budget/optical", json={
            "distance_km": 225000000,
            "scenario": "custom",
        })
        self.assertEqual(resp.status_code, 200)

    def test_rf_link_ka(self):
        resp = client.post("/api/link-budget/rf/ka", json={
            "scenario": "average",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["link_type"], "rf_ka")

    def test_rf_link_x(self):
        resp = client.post("/api/link-budget/rf/x", json={
            "scenario": "minimum",
        })
        self.assertEqual(resp.status_code, 200)

    def test_rf_link_invalid_band(self):
        resp = client.post("/api/link-budget/rf/invalid", json={
            "scenario": "average",
        })
        self.assertEqual(resp.status_code, 400)

    def test_link_budget_history(self):
        client.post("/api/link-budget/optical", json={"scenario": "average"})
        resp = client.get("/api/link-budget/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


class TestRoutingRouter(unittest.TestCase):

    def test_routing_decision(self):
        resp = client.post("/api/routing/decide", json={
            "current_node": "mars.areo.alpha",
            "neighbors": ["transit.esl4.relay", "mars.polar.gamma"],
            "link_qualities": {
                "transit.esl4.relay": 0.7,
                "mars.polar.gamma": 0.4,
            },
            "buffer_occupancy": 0.5,
            "bundle_priority": 2,
            "bundle_size_mb": 100,
            "bundle_deadline_hours": 12,
            "destination_node": "earth.dsn.goldstone",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("action", data)
        self.assertIn("confidence", data)
        self.assertIn("reasoning", data)

    def test_routing_decision_invalid_buffer(self):
        resp = client.post("/api/routing/decide", json={
            "current_node": "a",
            "neighbors": ["b"],
            "link_qualities": {"b": 0.5},
            "buffer_occupancy": 1.5,  # > 1.0
            "bundle_priority": 0,
            "bundle_size_mb": 10,
            "bundle_deadline_hours": 1,
            "destination_node": "c",
        })
        self.assertEqual(resp.status_code, 422)

    def test_routing_decision_invalid_priority(self):
        resp = client.post("/api/routing/decide", json={
            "current_node": "a",
            "neighbors": ["b"],
            "link_qualities": {"b": 0.5},
            "buffer_occupancy": 0.5,
            "bundle_priority": 99,  # > 4
            "bundle_size_mb": 10,
            "bundle_deadline_hours": 1,
            "destination_node": "c",
        })
        self.assertEqual(resp.status_code, 422)

    def test_list_decisions(self):
        resp = client.get("/api/routing/decisions")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_train_step(self):
        resp = client.post("/api/routing/train/step?episodes=10&epsilon=0.5")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("episodes", data)
        self.assertIn("total_episodes", data)


class TestOrbitalRouter(unittest.TestCase):

    def test_distance_default(self):
        resp = client.get("/api/orbital/distance")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("distance_km", data)
        self.assertIn("light_time_seconds", data)

    def test_distance_custom_anomaly(self):
        resp = client.get("/api/orbital/distance?true_anomaly_deg=90")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["true_anomaly_deg"], 90.0)

    def test_timeline(self):
        resp = client.get("/api/orbital/timeline?num_points=100")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(len(data["distances"]), 0)
        self.assertIn("min_distance_km", data)
        self.assertIn("max_distance_km", data)

    def test_contact_windows(self):
        resp = client.post("/api/orbital/contact-windows", json={
            "duration_days": 30,
            "min_elevation_deg": 10,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_contact_window_history(self):
        resp = client.get("/api/orbital/contact-windows/history")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


class TestSecurityRouter(unittest.TestCase):

    def test_qkd_bb84_no_eavesdropper(self):
        resp = client.post("/api/security/qkd", json={
            "protocol": "bb84",
            "num_qubits": 100,
            "channel_error": 0.02,
            "eavesdropper": False,
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("qber", data)
        self.assertIn("secure", data)

    def test_qkd_bb84_with_eavesdropper(self):
        resp = client.post("/api/security/qkd", json={
            "protocol": "bb84",
            "num_qubits": 100,
            "channel_error": 0.02,
            "eavesdropper": True,
        })
        self.assertEqual(resp.status_code, 200)
        # Eavesdropper should increase error rate
        data = resp.json()
        self.assertIsNotNone(data["qber"])

    def test_qkd_e91(self):
        resp = client.post("/api/security/qkd", json={
            "protocol": "e91",
            "num_qubits": 50,
            "channel_error": 0.01,
        })
        self.assertEqual(resp.status_code, 200)

    def test_qkd_sessions(self):
        client.post("/api/security/qkd", json={
            "protocol": "bb84",
            "num_qubits": 100,
        })
        resp = client.get("/api/security/qkd/sessions")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_qkd_invalid_num_qubits(self):
        resp = client.post("/api/security/qkd", json={
            "num_qubits": 0,  # < 1
        })
        self.assertEqual(resp.status_code, 422)


class TestCmdRouter(unittest.TestCase):

    def test_catalog(self):
        resp = client.get("/api/cmd/catalog")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("categories", data)
        self.assertIn("total", data)
        self.assertGreater(data["total"], 0)

    def test_catalog_has_categories(self):
        resp = client.get("/api/cmd/catalog")
        data = resp.json()
        for cat_key, cat in data["categories"].items():
            self.assertIn("label", cat)
            self.assertIn("commands", cat)
            for cmd in cat["commands"]:
                self.assertIn("id", cmd)
                self.assertIn("cmd", cmd)
                self.assertIn("description", cmd)

    def test_catalog_by_id(self):
        resp = client.get("/api/cmd/catalog/init")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("cmd", data)

    def test_catalog_unknown_id(self):
        resp = client.get("/api/cmd/catalog/nonexistent-command-id")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
