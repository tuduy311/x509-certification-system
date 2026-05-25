from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

def test_workflow():
    print("Testing Workflow...")

    # 1. Admin Login
    print("1. Admin Login")
    res = client.post("/api/auth/login", data={
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    })
    assert res.status_code == 200, res.text
    admin_token = res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Setup Root CA
    print("2. Setup Root CA")
    res = client.post("/api/admin/setup-root-ca", headers=admin_headers)
    assert res.status_code == 200, res.text
    print("Root CA setup successful.")

    # 3. Register Customer
    print("3. Register Customer")
    # Clean up user if exists
    # The simplest way is to register with a random name
    import random, string
    cust_username = "user_" + "".join(random.choices(string.ascii_lowercase, k=6))
    res = client.post("/api/auth/register", json={
        "username": cust_username,
        "password": "Customer@123"
    })
    assert res.status_code == 200, res.text

    # Login Customer
    res = client.post("/api/auth/login", data={
        "username": cust_username,
        "password": "Customer@123"
    })
    assert res.status_code == 200, res.text
    cust_token = res.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}

    # 4. Customer generates key
    print("4. Generate Customer Keys")
    res = client.post("/api/customer/generate-keys", headers=cust_headers, json={
        "algorithm": "RSA",
        "key_size": 2048,
        "description": "My test key"
    })
    assert res.status_code == 200, res.text
    keys = res.json()
    assert "private_key" in keys
    assert "public_key" in keys

    # 5. Customer creates a CSR using cryptography module directly (client side simulation)
    print("5. Customer generates CSR (simulated)")
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    from app.core.crypto_utils import generate_csr
    
    private_key = serialization.load_pem_private_key(keys["private_key"].encode("utf-8"), password=None, backend=default_backend())
    csr_pem = generate_csr(private_key, {"common_name": "test.com"})

    # 6. Customer requests certificate
    print("6. Request Certificate")
    res = client.post("/api/customer/request-certificate", headers=cust_headers, json={
        "csr_pem": csr_pem
    })
    assert res.status_code == 200, res.text
    req_id = res.json()["id"]

    # 7. Admin approves certificate
    print("7. Admin Approves Certificate")
    res = client.post(f"/api/admin/requests/{req_id}/approve", headers=admin_headers)
    assert res.status_code == 200, res.text
    cert_id = res.json()["id"]

    # 8. Customer revokes certificate
    print("8. Customer requests revocation")
    res = client.post(f"/api/customer/certificates/{cert_id}/request-revoke", headers=cust_headers, json={
        "reason": "Key Compromise"
    })
    assert res.status_code == 200, res.text
    revoke_req_id = res.json()["id"]

    # 9. Admin approves revocation
    print("9. Admin approves revocation")
    res = client.post(f"/api/admin/revocation-requests/{revoke_req_id}/approve", headers=admin_headers)
    assert res.status_code == 200, res.text

    # 10. Generate CRL
    print("10. Generate CRL")
    res = client.post("/api/admin/generate-crl", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert "crl_pem" in res.json()

    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    test_workflow()
