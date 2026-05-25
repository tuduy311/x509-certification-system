#!/usr/bin/env python3
"""
In-process tests for logout feature and password strength using FastAPI TestClient
(No external `requests` dependency required)
"""
import random
import string
from typing import Optional
from fastapi.testclient import TestClient

from backend.main import app
from backend.app.core.config import settings

client = TestClient(app)


def print_test(test_name: str):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")


def print_result(status: str, message: str):
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {message}")


def register(username: str, password: str):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def login(username: str, password: str):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def logout(token: str):
    return client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})


def change_password(token: str, old_password: str, new_password: str, confirm_new_password: str):
    return client.put(
        "/api/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": old_password,
            "new_password": new_password,
            "confirm_new_password": confirm_new_password
        }
    )


def get_my_requests(token: str):
    return client.get("/api/customer/my-requests", headers={"Authorization": f"Bearer {token}"})


def test_password_strength():
    print_test("Password Strength Validation")
    test_cases = [
        ("weak", False, "Too short (< 8 chars)"),
        ("weakpass", False, "No uppercase, no digit, no special char"),
        ("Weakpass", False, "No digit, no special char"),
        ("Weakpass1", False, "No special character"),
        ("Weak@Pass1", True, "Valid strong password"),
    ]

    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    for i, (password, should_pass, reason) in enumerate(test_cases):
        username = f"tc_pwd_{i}_{random_suffix}"
        res = register(username, password)
        if should_pass:
            if res.status_code == 200:
                print_result("PASS", f"Password '{password}' accepted ({reason})")
            else:
                print_result("FAIL", f"Password '{password}' rejected ({reason}) - {res.json().get('detail')}")
        else:
            if res.status_code == 400:
                print_result("PASS", f"Password '{password}' rejected ({reason})")
            else:
                print_result("FAIL", f"Password '{password}' accepted but should be rejected")


def test_logout_feature():
    print_test("Logout Feature")
    username = "test_logout_" + ''.join(random.choices(string.ascii_lowercase, k=6))
    password = "TestPass@123"

    # Register
    res = register(username, password)
    if res.status_code != 200:
        print_result("FAIL", f"Registration failed: {res.status_code} {res.text}")
        return
    print_result("PASS", "User registered successfully")

    # Login
    res = login(username, password)
    if res.status_code != 200:
        print_result("FAIL", f"Login failed: {res.status_code} {res.text}")
        return
    token = res.json()["access_token"]
    print_result("PASS", "User logged in successfully")

    # Access protected resource before logout
    res = get_my_requests(token)
    if res.status_code == 200:
        print_result("PASS", "Protected resource accessible before logout")
    else:
        print_result("FAIL", f"Protected resource failed before logout: {res.status_code} {res.text}")

    # Logout
    res = logout(token)
    if res.status_code == 200:
        print_result("PASS", "Logout successful")
    else:
        print_result("FAIL", f"Logout failed: {res.status_code} {res.text}")
        return

    # Access protected resource after logout (should be rejected)
    res = get_my_requests(token)
    if res.status_code == 401:
        print_result("PASS", "Protected resource correctly rejected after logout")
    else:
        print_result("FAIL", f"Protected resource still accessible after logout: {res.status_code}")


def test_change_password():
    print_test("Change Password with Validation")
    username = "test_change_" + ''.join(random.choices(string.ascii_lowercase, k=6))
    password = "OldPass@123"

    res = register(username, password)
    if res.status_code != 200:
        print_result("FAIL", f"Registration failed: {res.status_code} {res.text}")
        return
    print_result("PASS", "User registered")

    res = login(username, password)
    if res.status_code != 200:
        print_result("FAIL", f"Login failed: {res.status_code} {res.text}")
        return
    token = res.json()["access_token"]
    print_result("PASS", "User logged in")

    # Weak password change
    res = change_password(token, password, "weak", "weak")
    if res.status_code == 400:
        print_result("PASS", "Weak password rejected on change")
    else:
        print_result("FAIL", "Weak password accepted on change")

    # Strong password change
    res = change_password(token, password, "NewPass@456", "NewPass@456")
    if res.status_code == 200:
        print_result("PASS", "Strong password accepted on change")
    else:
        print_result("FAIL", f"Strong password rejected: {res.status_code} {res.text}")


if __name__ == "__main__":
    print("Make sure server is NOT running separately; TestClient runs in-process.")
    test_password_strength()
    test_logout_feature()
    test_change_password()
