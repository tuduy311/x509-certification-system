from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

def test():
    print("1. Admin Login")
    res = client.post("/api/auth/login", data={"username": settings.ADMIN_USERNAME, "password": settings.ADMIN_PASSWORD})
    assert res.status_code == 200, res.text
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    print("2. Setup Root CA")
    res = client.post("/api/admin/setup-root-ca", headers=admin_headers)
    assert res.status_code == 200, res.text

    print("3. Register Customer")
    import random, string
    cust_username = "user_" + "".join(random.choices(string.ascii_lowercase, k=6))
    res = client.post("/api/auth/register", json={"username": cust_username, "password": "Customer@123"})
    assert res.status_code == 200, res.text

    print("4. Customer Login")
    res = client.post("/api/auth/login", json={"username": cust_username, "password": "Customer@123"})
    assert res.status_code == 200, res.text
    cust_token = res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    print("5. Generate CSR")
    res = client.post("/api/customer/generate-csr", headers=cust_headers, json={"common_name": "test.com"})
    assert res.status_code == 200, res.text
    csr_pem = res.json()["csr_pem"]

    print("6. Request Certificate")
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={"csr_pem": csr_pem})
    assert res.status_code == 200, res.text
    req_id = res.json()["id"]

    print("7. Admin Approves Certificate")
    res = client.post(f"/api/admin/requests/{req_id}/approve", headers=admin_headers)
    assert res.status_code == 200, res.text
    cert_id = res.json()["id"]

    print("8. Download Certificate")
    res = client.get(f"/api/customer/certificates/{cert_id}/download", headers=cust_headers)
    assert res.status_code == 200, res.text
    assert "BEGIN CERTIFICATE" in res.text

    print("9. Admin Renews Certificate")
    res = client.post(f"/api/admin/certificates/{cert_id}/renew", headers=admin_headers)
    assert res.status_code == 200, res.text
    new_cert_id = res.json()["id"]

    print("10. Customer Requests Revocation")
    res = client.post(f"/api/customer/certificates/{new_cert_id}/request-revoke", headers=cust_headers, json={"reason": "Compromised"})
    assert res.status_code == 200, res.text
    rev_id = res.json()["id"]

    print("11. Admin Approves Revocation")
    res = client.post(f"/api/admin/revocation-requests/{rev_id}/approve", headers=admin_headers)
    assert res.status_code == 200, res.text

    print("12. Generate CRL")
    res = client.post("/api/admin/generate-crl", headers=admin_headers)
    assert res.status_code == 200, res.text

    print("13. Check Logs")
    res = client.get("/api/admin/logs", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert len(res.json()) > 0

    print("All Comprehensive Tests Passed!")

test()
