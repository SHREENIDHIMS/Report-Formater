from app.main import health


def test_health_endpoint_returns_ok() -> None:
    assert health() == {"status": "ok", "service": "vtu-report-studio-api"}
