"""Unit tests for the ErrorPayload schema v1.0.0."""

from datetime import datetime, UTC

from luca_core.schemas.error import (
    ErrorCategory,
    ErrorPayload,
    ErrorSeverity,
    create_user_error,
    create_system_error,
    create_timeout_error,
)


class TestErrorPayload:
    """Test suite for ErrorPayload schema."""

    def test_construction_with_defaults(self):
        """Test ErrorPayload construction with default values."""
        error = ErrorPayload(
            error_code="TEST_ERROR",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Test error message",
        )

        assert error.schema_version == "1.0.0"
        assert isinstance(error.timestamp, datetime)
        assert error.error_code == "TEST_ERROR"
        assert error.category == ErrorCategory.USER_ERROR
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test error message"
        assert error.remediation is None
        assert error.context_id is None
        assert error.context == {}
        assert error.recovery_hint is None

    def test_json_serialization_round_trip(self):
        """Test JSON serialization and deserialization."""
        original = ErrorPayload(
            error_code="JSON_TEST",
            category=ErrorCategory.SYSTEM_ERROR,
            severity=ErrorSeverity.WARNING,
            message="JSON test error",
            remediation="Check JSON format",
            context_id="ctx-123",
            context={"key": "value"},
        )

        # Serialize to JSON
        json_str = original.model_dump_json()
        # Deserialize from JSON
        loaded = ErrorPayload.model_validate_json(json_str)

        assert loaded.schema_version == original.schema_version
        assert loaded.error_code == original.error_code
        assert loaded.category == original.category
        assert loaded.severity == original.severity
        assert loaded.message == original.message
        assert loaded.remediation == original.remediation
        assert loaded.context_id == original.context_id
        assert loaded.context == original.context

    def test_schema_version_default(self):
        """Test that schema_version defaults to 1.0.0."""
        error = ErrorPayload(
            error_code="VERSION_TEST",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.INFO,
            message="Version test",
        )
        assert error.schema_version == "1.0.0"

    def test_timestamp_not_null(self):
        """Test that timestamp is never null and is timezone-aware."""
        error = ErrorPayload(
            error_code="TIMESTAMP_TEST",
            category=ErrorCategory.AUTH_ERROR,
            severity=ErrorSeverity.CRITICAL,
            message="Timestamp test",
        )
        assert error.timestamp is not None
        assert isinstance(error.timestamp, datetime)
        assert error.timestamp.tzinfo is not None
        assert error.timestamp.tzinfo == UTC

    def test_from_exception_method(self):
        """Test creating ErrorPayload from an exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error = ErrorPayload.from_exception(
                e,
                category=ErrorCategory.USER_ERROR,
                severity=ErrorSeverity.ERROR,
                error_code="EXCEPTION_TEST",
            )

        assert error.error_code == "EXCEPTION_TEST"
        assert error.category == ErrorCategory.USER_ERROR
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test exception"
        assert error.context["exception_type"] == "ValueError"

    def test_get_user_message_with_remediation(self):
        """Test get_user_message with remediation."""
        error = ErrorPayload(
            error_code="USER_MSG_TEST",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Invalid input",
            remediation="Please check your input format",
        )
        expected = "Invalid input - Please check your input format"
        assert error.get_user_message() == expected

    def test_get_user_message_with_recovery_hint_fallback(self):
        """Test get_user_message with deprecated recovery_hint."""
        error = ErrorPayload(
            error_code="RECOVERY_TEST",
            category=ErrorCategory.USER_ERROR,
            severity=ErrorSeverity.ERROR,
            message="Invalid input",
            recovery_hint="Legacy hint",
        )
        assert error.get_user_message() == "Invalid input - Legacy hint"

    def test_create_user_error_helper(self):
        """Test create_user_error helper function."""
        error = create_user_error(
            message="User error test",
            error_code="USER_HELPER_TEST",
            remediation="Fix the input",
        )
        assert error.error_code == "USER_HELPER_TEST"
        assert error.category == ErrorCategory.USER_ERROR
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "User error test"
        assert error.remediation == "Fix the input"

    def test_create_system_error_helper(self):
        """Test create_system_error helper function."""
        error = create_system_error(
            message="System error test",
            error_code="SYSTEM_HELPER_TEST",
            context={"detail": "test context"},
        )
        assert error.error_code == "SYSTEM_HELPER_TEST"
        assert error.category == ErrorCategory.SYSTEM_ERROR
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "System error test"
        assert error.context == {"detail": "test context"}

    def test_create_timeout_error_helper(self):
        """Test create_timeout_error helper function."""
        error = create_timeout_error(
            operation="test_operation",
            timeout_seconds=30,
        )
        assert error.error_code == "OPERATION_TIMEOUT"
        assert error.category == ErrorCategory.TIMEOUT_ERROR
        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Operation 'test_operation' timed out after 30 seconds"
        expected = "Try again with a longer timeout or simplify the request"
        assert error.remediation == expected