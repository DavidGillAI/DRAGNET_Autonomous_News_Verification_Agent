"""Offline HTTP contract checks; the research graph is replaced before import."""

import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        graph_module = types.ModuleType("src.dragnet_langgraph")
        graph_module.dragnet_graph = Mock()
        with patch.dict(sys.modules, {"src.dragnet_langgraph": graph_module}):
            cls.api = importlib.import_module("src.api")
        cls.graph = graph_module.dragnet_graph
        cls.client = TestClient(cls.api.app)

    def setUp(self):
        self.graph.reset_mock()
        self.graph.invoke.side_effect = None
        self.graph.invoke.return_value = {
            "final_report": "Example report",
            "research_query": "example search",
            "validation_passed": True,
            "research_iteration_count": 1,
        }

    def test_success_preserves_report_and_metadata(self):
        response = self.client.post("/investigate", json={"query": "  A question?  "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "report": "Example report",
            "planned_search": "example search",
            "validation_passed": True,
            "research_iterations": 1,
        })
        self.graph.invoke.assert_called_once_with({"query": "A question?", "iteration_count": 0})

    def test_maximum_length_is_accepted(self):
        response = self.client.post("/investigate", json={"query": "x" * 4000})
        self.assertEqual(response.status_code, 200)
        self.graph.invoke.assert_called_once()

    def test_invalid_inputs_never_start_research(self):
        for body in ({}, {"query": ""}, {"query": " \t\n"},
                     {"query": "x" * 4001}, {"query": None},
                     {"query": 123}, {"query": True}, {"query": []}, []):
            with self.subTest(body_type=type(body).__name__):
                response = self.client.post("/investigate", json=body)
                self.assertEqual(response.status_code, 422)
                self.assertFalse(response.json()["validation_passed"])
                self.assertIn("report", response.json())
                self.graph.invoke.assert_not_called()

    def test_malformed_json_returns_safe_report(self):
        response = self.client.post("/investigate", content="{broken",
                                    headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("report", response.json())
        self.graph.invoke.assert_not_called()

    def test_exception_is_not_returned_or_logged(self):
        private_detail = "provider-url?apikey=fake-private-value"
        self.graph.invoke.side_effect = RuntimeError(private_detail)
        with self.assertLogs(self.api.logger, level="ERROR") as logs:
            response = self.client.post("/investigate", json={"query": "A question?"})
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.json()["validation_passed"])
        self.assertIn("report", response.json())
        self.assertNotIn(private_detail, response.text)
        self.assertNotIn(private_detail, " ".join(logs.output))

    def test_unvalidated_draft_is_not_a_transport_failure(self):
        self.graph.invoke.return_value = {"final_report": "Draft needing review"}
        response = self.client.post("/investigate", json={"query": "A question?"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["validation_passed"])


if __name__ == "__main__":
    unittest.main()
