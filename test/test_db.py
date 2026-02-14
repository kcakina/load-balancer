from app.db import DB


class TestValidateInput:
    def setup_method(self):
        self.db = DB()

    def test_valid_input(self):
        assert self.db.validate_input("user1", 5, 10) is True

    def test_empty_key(self):
        assert self.db.validate_input("", 5, 10) is False

    def test_zero_limit(self):
        assert self.db.validate_input("user1", 0, 10) is False

    def test_negative_limit(self):
        assert self.db.validate_input("user1", -1, 10) is False

    def test_zero_window(self):
        assert self.db.validate_input("user1", 5, 0) is False

    def test_negative_window(self):
        assert self.db.validate_input("user1", 5, -1) is False


class TestCheck:
    def setup_method(self):
        self.db = DB()

    def test_first_check_allowed(self):
        result = self.db.check("user1", 2, 10)
        assert result.allowed is True
        assert result.remaining == 1

    def test_second_check_allowed(self):
        self.db.check("user1", 2, 10)
        result = self.db.check("user1", 2, 10)
        assert result.allowed is True
        assert result.remaining == 0

    def test_third_check_blocked(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)
        result = self.db.check("user1", 2, 10)
        assert result.allowed is False
        assert result.remaining == 0

    def test_window_reset(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)

        # Simulate window expiry by backdating start_ts
        state_key = ("user1", 2, 10)
        self.db.state[state_key].start_ts -= 10

        result = self.db.check("user1", 2, 10)
        assert result.allowed is True
        assert result.remaining == 1

    def test_different_keys_isolated(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)

        result = self.db.check("user2", 2, 10)
        assert result.allowed is True
        assert result.remaining == 1

    def test_same_key_different_limit_tracked_independently(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)

        result = self.db.check("user1", 5, 10)
        assert result.allowed is True
        assert result.remaining == 4

    def test_same_key_different_window_tracked_independently(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)

        result = self.db.check("user1", 2, 30)
        assert result.allowed is True
        assert result.remaining == 1

    def test_reset_in_seconds(self):
        result = self.db.check("user1", 2, 10)
        assert result.reset_in_seconds == 10

    def test_reset_in_seconds_after_blocked(self):
        self.db.check("user1", 2, 10)
        self.db.check("user1", 2, 10)
        result = self.db.check("user1", 2, 10)
        assert result.reset_in_seconds <= 10
        assert result.reset_in_seconds > 0