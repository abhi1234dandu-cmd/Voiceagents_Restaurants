from app.services.plan_limits import can_activate_agent, can_add_location, limits_for, minutes_remaining


def test_starter_limits():
    assert limits_for("starter")["minutes"] == 500
    assert limits_for("starter")["locations"] == 1
    assert limits_for("starter")["sms"] is False


def test_professional_sms():
    assert limits_for("professional")["sms"] is True
    assert limits_for("professional")["minutes"] == 2000


def test_minutes_remaining():
    assert minutes_remaining("starter", 100) == 400
    assert minutes_remaining("premium", 99999) is None


def test_activate_blocked_when_exhausted():
    ok, _ = can_activate_agent({"plan": "starter", "status": "active"}, 500)
    assert ok is False


def test_location_cap():
    ok, _ = can_add_location({"plan": "starter"}, 1)
    assert ok is False
    ok, _ = can_add_location({"plan": "premium"}, 5)
    assert ok is True
