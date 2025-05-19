"""Tests to improve coverage for context schemas."""

from luca_core.schemas.context import Project


class TestContextCoverage:
    """Test context schema edge cases for coverage."""

    def test_project_export_ticket(self):
        """Test export_ticket method."""
        project = Project(id="proj-123", name="Test Project", user_id="user-456")

        ticket = project.export_ticket()
        assert ticket == "Ticket for project Test Project (ID: proj-123)"
