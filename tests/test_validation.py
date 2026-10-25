from utils.validators import (
    validate_email,
    validate_password,
    validate_phone,
    validate_date,
    validate_file,
    sanitize_string,
    validate_required
)

def test_validate_email():
    assert validate_email("user@example.com") is True
    assert validate_email("user.name+tag@sub.domain.org") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@no-local-part.com") is False

def test_validate_password():
    # Min 8 chars, uppercase, lowercase, number, special char
    assert validate_password("Strong@123") is True
    assert validate_password("Secret#2026") is True
    # Short
    assert validate_password("Short1!") is False
    # No uppercase
    assert validate_password("lowercase@123") is False
    # No lowercase
    assert validate_password("UPPERCASE@123") is False
    # No digit
    assert validate_password("NoDigits@Pass") is False
    # No special char
    assert validate_password("NoSpecial123") is False

def test_validate_phone():
    assert validate_phone("+91 9876543210") is True
    assert validate_phone("9876543210") is True
    assert validate_phone("123") is False
    assert validate_phone("abc1234567") is False

def test_validate_date():
    assert validate_date("2026-06-15") is True
    assert validate_date("not-a-date") is False
    assert validate_date("2026-02-31") is False

def test_validate_file():
    # Valid types: pdf, jpg, jpeg, png (size <= 10MB)
    assert validate_file("report.pdf", 5000) is True
    assert validate_file("scan.png", 100000) is True
    assert validate_file("photo.jpg", 200000) is True
    assert validate_file("virus.exe", 5000) is False
    assert validate_file("script.sh", 5000) is False
    # Size limit (10MB = 10485760 bytes)
    assert validate_file("huge.pdf", 20000000) is False

def test_sanitize_string():
    dirty = "<script>alert('xss')</script>"
    clean = sanitize_string(dirty)
    assert "<" not in clean
    assert ">" not in clean
    assert "&lt;script&gt;" in clean

def test_validate_required():
    data = {'name': 'Rajesh', 'email': 'rajesh@example.com', 'age': '40'}
    valid, missing = validate_required(data, ['name', 'email'])
    assert valid is True
    assert len(missing) == 0

    valid, missing = validate_required(data, ['name', 'phone'])
    assert valid is False
    assert 'phone' in missing
