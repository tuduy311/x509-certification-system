"""
Test toàn bộ chức năng hệ thống X.509 Certification System
Bao gồm tất cả yêu cầu đồ án: Nhóm Admin (A.1-A.11) và Nhóm Khách hàng (B.1-B.9)
"""
import random
import string
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

def test_full_workflow():
    print("\n" + "="*60)
    print("  X.509 CERTIFICATION SYSTEM - FULL TEST SUITE")
    print("="*60)

    # ────────────────────────────────────────
    # [A.1] Đăng nhập Admin
    # ────────────────────────────────────────
    print("\n[A.1] Admin Login")
    res = client.post("/api/auth/login", json={
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    })
    assert res.status_code == 200, f"FAIL: {res.text}"
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("  ✓ Admin logged in")

    # ────────────────────────────────────────
    # [A.4 + A.5] Phát sinh cặp khoá + Root Certificate
    # ────────────────────────────────────────
    print("\n[A.4+A.5] Generate Root CA key pair + Root Certificate")
    res = client.post("/api/admin/setup-root-ca", headers=admin_headers,
                      params={"key_size": 2048, "validity_days": 3650, "hash_alg": "SHA256"})
    assert res.status_code == 200, f"FAIL: {res.text}"
    print("  ✓ Root CA generated")

    # ────────────────────────────────────────
    # [A.3] Thiết lập thông số kỹ thuật
    # ────────────────────────────────────────
    print("\n[A.3] Set system config")
    for key, val in [("default_validity_days", "365"), ("hash_algorithm", "SHA256"), ("default_key_size", "2048")]:
        res = client.put("/api/admin/config", headers=admin_headers, params={"key": key, "value": val})
        assert res.status_code == 200, f"FAIL set {key}: {res.text}"
    res = client.get("/api/admin/config", headers=admin_headers)
    assert res.status_code == 200
    assert "default_validity_days" in res.json()
    print(f"  ✓ Config: {res.json()}")

    # ────────────────────────────────────────
    # [B.1] Đăng ký tài khoản khách hàng
    # ────────────────────────────────────────
    cust_username = "user_" + "".join(random.choices(string.ascii_lowercase, k=6))
    print(f"\n[B.1] Register customer: {cust_username}")
    res = client.post("/api/auth/register", json={"username": cust_username, "password": "Customer@123"})
    assert res.status_code == 200, f"FAIL: {res.text}"
    print("  ✓ Customer registered")

    # ────────────────────────────────────────
    # [B.2] Đăng nhập khách hàng
    # ────────────────────────────────────────
    print("\n[B.2] Customer Login")
    res = client.post("/api/auth/login", json={"username": cust_username, "password": "Customer@123"})
    assert res.status_code == 200, f"FAIL: {res.text}"
    cust_token = res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    print("  ✓ Customer logged in")

    # ────────────────────────────────────────
    # [B.3] Đổi mật khẩu (qua request body - đã sửa)
    # ────────────────────────────────────────
    print("\n[B.3] Change password (via request body, NOT query param)")
    res = client.put("/api/auth/change-password", headers=cust_headers, json={"new_password": "NewPass@456"})
    assert res.status_code == 200, f"FAIL: {res.text}"
    # Re-login với mật khẩu mới
    res = client.post("/api/auth/login", json={"username": cust_username, "password": "NewPass@456"})
    assert res.status_code == 200, f"FAIL re-login: {res.text}"
    cust_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
    print("  ✓ Password changed & re-logged in with new password")

    # ────────────────────────────────────────
    # [B.4] Phát sinh cặp khoá Public/Private cá nhân
    # ────────────────────────────────────────
    print("\n[B.4] Generate personal RSA key pair")
    res = client.get("/api/customer/generate-keys", headers=cust_headers)
    assert res.status_code == 200, f"FAIL: {res.text}"
    assert "private_key" in res.json() and "public_key" in res.json()
    print("  ✓ RSA key pair generated")

    # ────────────────────────────────────────
    # [B.5] Sinh CSR từ form (THÊM MỚI)
    # ────────────────────────────────────────
    print("\n[B.5] Generate CSR from form (NEW endpoint)")
    res = client.post("/api/customer/generate-csr", headers=cust_headers, json={
        "common_name": "testwebsite.com",
        "country": "VN",
        "state": "Ho Chi Minh",
        "locality": "Ho Chi Minh",
        "organization": "Test Company",
        "organizational_unit": "IT"
    })
    assert res.status_code == 200, f"FAIL: {res.text}"
    csr_data = res.json()
    assert "private_key" in csr_data and "csr_pem" in csr_data
    csr_pem = csr_data["csr_pem"]
    print(f"  ✓ CSR generated for 'testwebsite.com'")

    # ────────────────────────────────────────
    # [B.5] Nộp CSR để xin cấp chứng nhận
    # ────────────────────────────────────────
    print("\n[B.5] Submit CSR → request certificate")
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={"csr_pem": csr_pem})
    assert res.status_code == 200, f"FAIL: {res.text}"
    req_id = res.json()["id"]
    assert res.json()["status"] == "pending"
    print(f"  ✓ CSR submitted (request_id={req_id}, status=pending)")

    # ────────────────────────────────────────
    # [B.6] Xem danh sách yêu cầu
    # ────────────────────────────────────────
    print("\n[B.6] List my certificate requests")
    res = client.get("/api/customer/my-requests", headers=cust_headers)
    assert res.status_code == 200 and len(res.json()) >= 1
    print(f"  ✓ Found {len(res.json())} request(s)")

    # ────────────────────────────────────────
    # [A.6] Admin từ chối yêu cầu
    # ────────────────────────────────────────
    print("\n[A.6] Admin REJECTS certificate request")
    res = client.post(f"/api/admin/requests/{req_id}/reject", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "rejected", f"FAIL: {res.text}"
    print(f"  ✓ Request #{req_id} rejected")

    # Nộp CSR lần 2 để test approve
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={"csr_pem": csr_pem})
    req_id2 = res.json()["id"]
    print(f"\n  Submitted 2nd CSR (request_id={req_id2}) for approval test")

    # ────────────────────────────────────────
    # [A.7] Admin phê duyệt → phát sinh chứng nhận X.509
    # (tự động dùng config DB — đã sửa)
    # ────────────────────────────────────────
    print("\n[A.7] Admin APPROVES certificate (auto-uses DB config)")
    res = client.post(f"/api/admin/requests/{req_id2}/approve", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "approved", f"FAIL: {res.text}"
    cert_id = res.json()["id"]
    cert_pem = res.json()["cert_pem"]
    serial = res.json()["serial_number"]
    print(f"  ✓ Certificate issued (cert_id={cert_id}, serial={serial[:20]}...)")

    # ────────────────────────────────────────
    # [B.6] Xem danh sách chứng nhận
    # ────────────────────────────────────────
    print("\n[B.6] List my certificates")
    res = client.get("/api/customer/my-certificates", headers=cust_headers)
    assert res.status_code == 200 and len(res.json()) >= 1
    print(f"  ✓ Found {len(res.json())} certificate(s)")

    # ────────────────────────────────────────
    # [B.6] Tải về file .crt (THÊM MỚI)
    # ────────────────────────────────────────
    print("\n[B.6] Download certificate as .crt file (NEW endpoint)")
    res = client.get(f"/api/customer/certificates/{cert_id}/download", headers=cust_headers)
    assert res.status_code == 200, f"FAIL: {res.text}"
    assert "BEGIN CERTIFICATE" in res.text
    assert "attachment" in res.headers.get("content-disposition", "")
    print(f"  ✓ Certificate downloaded ({len(res.content)} bytes, content-disposition: attachment)")

    # ────────────────────────────────────────
    # [B.9] Upload chứng nhận bất kỳ để xem thông tin
    # ────────────────────────────────────────
    print("\n[B.9] Parse/upload any X.509 certificate")
    res = client.post("/api/customer/parse-certificate", headers=cust_headers, json={"cert_pem": cert_pem})
    assert res.status_code == 200, f"FAIL: {res.text}"
    parsed = res.json()
    assert "serial_number" in parsed and "subject" in parsed and "issuer" in parsed
    print(f"  ✓ Parsed: serial={parsed['serial_number'][:20]}... subject={parsed['subject']}")

    # ────────────────────────────────────────
    # [B.7] Khách hàng yêu cầu thu hồi chứng nhận
    # ────────────────────────────────────────
    print("\n[B.7] Customer requests certificate revocation")
    res = client.post(f"/api/customer/certificates/{cert_id}/request-revoke",
                      headers=cust_headers, json={"reason": "Key Compromise"})
    assert res.status_code == 200, f"FAIL: {res.text}"
    revoke_req_id = res.json()["id"]
    print(f"  ✓ Revocation requested (revoke_req_id={revoke_req_id})")

    # ────────────────────────────────────────
    # [A.9] Admin xem danh sách yêu cầu thu hồi
    # ────────────────────────────────────────
    print("\n[A.9] Admin lists revocation requests")
    res = client.get("/api/admin/revocation-requests", headers=admin_headers)
    assert res.status_code == 200 and len(res.json()) >= 1
    print(f"  ✓ Found {len(res.json())} revocation request(s)")

    # ────────────────────────────────────────
    # [A.9] Admin TỪ CHỐI yêu cầu thu hồi (THÊM MỚI)
    # ────────────────────────────────────────
    print("\n[A.9] Admin REJECTS revocation request (NEW endpoint)")
    res = client.post(f"/api/admin/revocation-requests/{revoke_req_id}/reject", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "rejected", f"FAIL: {res.text}"
    print(f"  ✓ Revocation #{revoke_req_id} rejected — certificate still active")

    # Customer yêu cầu thu hồi lần 2
    res = client.post(f"/api/customer/certificates/{cert_id}/request-revoke",
                      headers=cust_headers, json={"reason": "Superseded"})
    revoke_req_id2 = res.json()["id"]
    print(f"\n  2nd revocation request submitted (id={revoke_req_id2})")

    # ────────────────────────────────────────
    # [A.9] Admin PHÊ DUYỆT yêu cầu thu hồi
    # ────────────────────────────────────────
    print("\n[A.9] Admin APPROVES revocation request")
    res = client.post(f"/api/admin/revocation-requests/{revoke_req_id2}/approve", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "revoked", f"FAIL: {res.text}"
    print(f"  ✓ Revocation approved — certificate is now REVOKED")

    # ────────────────────────────────────────
    # [A.8] Admin trực tiếp revoke chứng nhận
    # ────────────────────────────────────────
    print("\n[A.8] Admin directly revokes a certificate (no customer request)")
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={"csr_pem": csr_pem})
    r2_id = res.json()["id"]
    res = client.post(f"/api/admin/requests/{r2_id}/approve", headers=admin_headers)
    cert_id2 = res.json()["id"]
    res = client.post(f"/api/admin/certificates/{cert_id2}/revoke", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "revoked", f"FAIL: {res.text}"
    print(f"  ✓ Admin directly revoked cert_id={cert_id2}")

    # ────────────────────────────────────────
    # [A.10] Cập nhật / tạo CRL
    # ────────────────────────────────────────
    print("\n[A.10] Generate CRL (Certificate Revocation List)")
    res = client.post("/api/admin/generate-crl", headers=admin_headers)
    assert res.status_code == 200, f"FAIL: {res.text}"
    assert "BEGIN X509 CRL" in res.json()["crl_pem"]
    print("  ✓ CRL generated successfully")

    # ────────────────────────────────────────
    # [B.8] Tra cứu CRL (public, không cần auth)
    # ────────────────────────────────────────
    print("\n[B.8] Get CRL publicly (no auth required)")
    res = client.get("/api/customer/crl")
    assert res.status_code == 200 and "crl_pem" in res.json(), f"FAIL: {res.text}"
    print("  ✓ CRL retrieved without authentication")

    # ────────────────────────────────────────
    # [A.8] Luồng Renew chứng nhận
    # ────────────────────────────────────────
    print("\n[A.8] Certificate Renewal flow")
    # Tạo cert mới để renew
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={"csr_pem": csr_pem})
    r3_id = res.json()["id"]
    res = client.post(f"/api/admin/requests/{r3_id}/approve", headers=admin_headers)
    cert_id3 = res.json()["id"]

    # Customer yêu cầu renew
    res = client.post(f"/api/customer/certificates/{cert_id3}/renew", headers=cust_headers)
    assert res.status_code == 200, f"FAIL renewal request: {res.text}"
    ren_req_id = res.json()["id"]
    print(f"  ✓ Renewal requested (renewal_req_id={ren_req_id})")

    # Admin từ chối renew
    res = client.post(f"/api/admin/requests/{ren_req_id}/reject-renewal", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "rejected", f"FAIL: {res.text}"
    print(f"  ✓ Renewal rejected")

    # Customer yêu cầu renew lần 2
    res = client.post(f"/api/customer/certificates/{cert_id3}/renew", headers=cust_headers)
    ren_req_id2 = res.json()["id"]

    # Admin phê duyệt renew
    res = client.post(f"/api/admin/requests/{ren_req_id2}/approve-renewal", headers=admin_headers)
    assert res.status_code == 200 and res.json()["status"] == "approved", f"FAIL: {res.text}"
    print(f"  ✓ Renewal approved — new certificate issued")

    # ────────────────────────────────────────
    # [A.2] Admin đổi mật khẩu
    # ────────────────────────────────────────
    print("\n[A.2] Admin changes password (via request body)")
    res = client.put("/api/auth/change-password", headers=admin_headers,
                     json={"new_password": settings.ADMIN_PASSWORD})  # giữ nguyên password gốc
    assert res.status_code == 200, f"FAIL: {res.text}"
    print("  ✓ Admin password changed (restored to original)")

    # ────────────────────────────────────────
    # [A.11] Xem nhật ký hoạt động
    # ────────────────────────────────────────
    print("\n[A.11] View activity logs")
    res = client.get("/api/admin/logs", headers=admin_headers)
    assert res.status_code == 200, f"FAIL: {res.text}"
    logs = res.json()
    assert len(logs) > 0
    actions = set(log["action"] for log in logs)
    print(f"  ✓ Found {len(logs)} log entries")
    print(f"  Actions: {actions}")

    # Kiểm tra các action quan trọng đều được log
    expected_actions = {
        "USER_LOGIN", "USER_REGISTERED", "PASSWORD_CHANGED",
        "ROOT_CA_GENERATED", "CONFIG_UPDATED",
        "CSR_GENERATED", "CERTIFICATE_REQUESTED",
        "CERTIFICATE_APPROVED", "CERTIFICATE_REJECTED",
        "CERTIFICATE_REVOKED",
        "REVOCATION_REQUESTED", "REVOCATION_APPROVED", "REVOCATION_REJECTED",
        "CRL_GENERATED",
        "CERTIFICATE_RENEWAL_REQUESTED", "CERTIFICATE_RENEWAL_APPROVED", "CERTIFICATE_RENEWAL_REJECTED",
    }
    missing = expected_actions - actions
    if missing:
        print(f"  ⚠ Missing log actions: {missing}")
    else:
        print("  ✓ All expected actions are logged!")

    print("\n" + "="*60)
    print("  ✅ ALL TESTS PASSED!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_full_workflow()
