
from app.db.crud import log_guardrail_decision
from app.db.database import Base, SessionLocal, engine
from app.db.models import GuardrailDecision


def test_log_guardrail_decision_persists_blocked_decision():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        log_guardrail_decision(
            db=db,
            request_id="TEST-LOG-001",
            control="PROMPT_INJECTION",
            outcome="BLOCKED",
            reason_code="PROMPT_INJECTION_DETECTED",
        )

        result = (
            db.query(GuardrailDecision)
            .filter(
                GuardrailDecision.request_id == "TEST-LOG-001"
            )
            .first()
        )

        assert result is not None
        assert result.request_id == "TEST-LOG-001"
        assert result.control == "PROMPT_INJECTION"
        assert result.outcome == "BLOCKED"
        assert result.reason_code == "PROMPT_INJECTION_DETECTED"

    finally:
        db.query(GuardrailDecision).filter(
            GuardrailDecision.request_id == "TEST-LOG-001"
        ).delete()
        db.commit()
        db.close()


def test_log_guardrail_decision_persists_allowed_decision():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        log_guardrail_decision(
            db=db,
            request_id="TEST-LOG-002",
            control="GUARDRAIL",
            outcome="ALLOWED",
            reason_code="SAFE_INPUT",
        )

        result = (
            db.query(GuardrailDecision)
            .filter(
                GuardrailDecision.request_id == "TEST-LOG-002"
            )
            .first()
        )

        assert result is not None
        assert result.request_id == "TEST-LOG-002"
        assert result.control == "GUARDRAIL"
        assert result.outcome == "ALLOWED"
        assert result.reason_code == "SAFE_INPUT"

    finally:
        db.query(GuardrailDecision).filter(
            GuardrailDecision.request_id == "TEST-LOG-002"
        ).delete()
        db.commit()
        db.close()


def test_guardrail_decision_schema_excludes_question_content():
    column_names = {
        column.name
        for column in GuardrailDecision.__table__.columns
    }

    sensitive_content_fields = {
        "question",
        "user_question",
        "prompt",
        "user_prompt",
        "input_text",
        "content",
    }

    assert column_names.isdisjoint(sensitive_content_fields)

    assert {
        "request_id",
        "control",
        "outcome",
        "reason_code",
        "timestamp",
    }.issubset(column_names)