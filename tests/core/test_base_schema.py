"""Tests for base schema definitions."""

import pytest

from luca_core.schemas.base import (
    AgentRole,
    CompletionStatus,
    DomainType,
    LearningMode,
    SeverityLevel,
)


class TestSeverityLevel:
    """Test SeverityLevel enum."""

    def test_severity_levels(self):
        """Test all severity levels are accessible."""
        assert SeverityLevel.INFO == "info"
        assert SeverityLevel.WARNING == "warning"
        assert SeverityLevel.ERROR == "error"
        assert SeverityLevel.CRITICAL == "critical"

    def test_severity_level_values(self):
        """Test severity level string values."""
        assert SeverityLevel.INFO.value == "info"
        assert SeverityLevel.WARNING.value == "warning"
        assert SeverityLevel.ERROR.value == "error"
        assert SeverityLevel.CRITICAL.value == "critical"

    def test_severity_level_from_string(self):
        """Test creating severity level from string."""
        assert SeverityLevel("info") == SeverityLevel.INFO
        assert SeverityLevel("warning") == SeverityLevel.WARNING
        assert SeverityLevel("error") == SeverityLevel.ERROR
        assert SeverityLevel("critical") == SeverityLevel.CRITICAL


class TestCompletionStatus:
    """Test CompletionStatus enum."""

    def test_completion_statuses(self):
        """Test all completion statuses are accessible."""
        assert CompletionStatus.SUCCESS == "success"
        assert CompletionStatus.PARTIAL == "partial"
        assert CompletionStatus.FAILURE == "failure"

    def test_completion_status_values(self):
        """Test completion status string values."""
        assert CompletionStatus.SUCCESS.value == "success"
        assert CompletionStatus.PARTIAL.value == "partial"
        assert CompletionStatus.FAILURE.value == "failure"

    def test_completion_status_from_string(self):
        """Test creating completion status from string."""
        assert CompletionStatus("success") == CompletionStatus.SUCCESS
        assert CompletionStatus("partial") == CompletionStatus.PARTIAL
        assert CompletionStatus("failure") == CompletionStatus.FAILURE


class TestDomainType:
    """Test DomainType enum."""

    def test_domain_types(self):
        """Test all domain types are accessible."""
        assert DomainType.GENERAL == "general"
        assert DomainType.WEB == "web"
        assert DomainType.DATA_SCIENCE == "data_science"
        assert DomainType.QUANTITATIVE_FINANCE == "quantitative_finance"

    def test_domain_type_values(self):
        """Test domain type string values."""
        assert DomainType.GENERAL.value == "general"
        assert DomainType.WEB.value == "web"
        assert DomainType.DATA_SCIENCE.value == "data_science"
        assert DomainType.QUANTITATIVE_FINANCE.value == "quantitative_finance"

    def test_domain_type_from_string(self):
        """Test creating domain type from string."""
        assert DomainType("general") == DomainType.GENERAL
        assert DomainType("web") == DomainType.WEB
        assert DomainType("data_science") == DomainType.DATA_SCIENCE
        assert DomainType("quantitative_finance") == DomainType.QUANTITATIVE_FINANCE


class TestLearningMode:
    """Test LearningMode enum."""

    def test_learning_modes(self):
        """Test all learning modes are accessible."""
        assert LearningMode.NOOB == "noob"
        assert LearningMode.PRO == "pro"
        assert LearningMode.GURU == "guru"

    def test_learning_mode_values(self):
        """Test learning mode string values."""
        assert LearningMode.NOOB.value == "noob"
        assert LearningMode.PRO.value == "pro"
        assert LearningMode.GURU.value == "guru"

    def test_learning_mode_from_string(self):
        """Test creating learning mode from string."""
        assert LearningMode("noob") == LearningMode.NOOB
        assert LearningMode("pro") == LearningMode.PRO
        assert LearningMode("guru") == LearningMode.GURU


class TestAgentRole:
    """Test AgentRole enum."""

    def test_agent_roles(self):
        """Test all agent roles are accessible."""
        assert AgentRole.MANAGER == "manager"
        assert AgentRole.DEVELOPER == "developer"
        assert AgentRole.QA == "qa"
        assert AgentRole.DOC_WRITER == "doc_writer"
        assert AgentRole.ANALYST == "analyst"
        assert AgentRole.CUSTOM == "custom"

    def test_agent_role_values(self):
        """Test agent role string values."""
        assert AgentRole.MANAGER.value == "manager"
        assert AgentRole.DEVELOPER.value == "developer"
        assert AgentRole.QA.value == "qa"
        assert AgentRole.DOC_WRITER.value == "doc_writer"
        assert AgentRole.ANALYST.value == "analyst"
        assert AgentRole.CUSTOM.value == "custom"

    def test_agent_role_from_string(self):
        """Test creating agent role from string."""
        assert AgentRole("manager") == AgentRole.MANAGER
        assert AgentRole("developer") == AgentRole.DEVELOPER
        assert AgentRole("qa") == AgentRole.QA
        assert AgentRole("doc_writer") == AgentRole.DOC_WRITER
        assert AgentRole("analyst") == AgentRole.ANALYST
        assert AgentRole("custom") == AgentRole.CUSTOM


class TestEnumErrorHandling:
    """Test error handling for all enums."""

    def test_invalid_severity_level(self):
        """Test invalid severity level raises error."""
        with pytest.raises(ValueError):
            SeverityLevel("invalid")

    def test_invalid_completion_status(self):
        """Test invalid completion status raises error."""
        with pytest.raises(ValueError):
            CompletionStatus("invalid")

    def test_invalid_domain_type(self):
        """Test invalid domain type raises error."""
        with pytest.raises(ValueError):
            DomainType("invalid")

    def test_invalid_learning_mode(self):
        """Test invalid learning mode raises error."""
        with pytest.raises(ValueError):
            LearningMode("invalid")

    def test_invalid_agent_role(self):
        """Test invalid agent role raises error."""
        with pytest.raises(ValueError):
            AgentRole("invalid")
