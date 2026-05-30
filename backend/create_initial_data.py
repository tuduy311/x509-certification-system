from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import models
from app.core import security
from app.core.config import settings
from app.db.database import engine

models.Base.metadata.create_all(bind=engine)


def init_db(db: Session) -> None:
    admin_username = settings.ADMIN_USERNAME
    admin_password = settings.ADMIN_PASSWORD
    
    user = db.query(models.User).filter(models.User.username == admin_username).first()
    if not user:
        user = models.User(
            username=admin_username,
            hashed_password=security.get_password_hash(admin_password),
            role=models.Role.ADMIN
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Admin user '{admin_username}' created successfully")

    default_configs = {
        "default_validity_days": "365",
        "asymmetric_algorithm": "RSA",
        "hash_algorithm": "SHA256",
        "key_length": "2048",
        "crl_lifetime_days": "365",
        "max_cert_validity_days": "3650",
        "min_key_length": "2048",
        "enable_ecc": "true",
        "enable_rsa": "true",
        "certificate_version": "3",
    }

    for key, val in default_configs.items():
        cfg = db.query(models.SystemConfig).filter(models.SystemConfig.key == key).first()
        if not cfg:
            cfg = models.SystemConfig(key=key, value=val, default_value=val)
            db.add(cfg)
        else:
            cfg.default_value = val
    db.commit()
    print("System configurations seeded successfully")

    asym_algos = ["RSA", "ECC"]
    for name in asym_algos:
        alg = db.query(models.AsymmetricAlgorithm).filter(models.AsymmetricAlgorithm.name == name).first()
        if not alg:
            alg = models.AsymmetricAlgorithm(name=name, is_active=True)
            db.add(alg)
    db.commit()
    print("Asymmetric algorithms seeded successfully")

    hash_algos = ["SHA256", "SHA384", "SHA512"]
    for name in hash_algos:
        alg = db.query(models.HashAlgorithm).filter(models.HashAlgorithm.name == name).first()
        if not alg:
            alg = models.HashAlgorithm(name=name, is_active=True)
            db.add(alg)
    db.commit()
    print("Hash algorithms seeded successfully")

    key_lengths = [
        {"value": 2048, "algo_name": "RSA"},
        {"value": 3072, "algo_name": "RSA"},
        {"value": 4096, "algo_name": "RSA"},
        {"value": 256, "algo_name": "ECC"},
        {"value": 384, "algo_name": "ECC"},
        {"value": 521, "algo_name": "ECC"},
    ]
    for kl in key_lengths:
        len_obj = db.query(models.KeyLength).filter(
            models.KeyLength.value == kl["value"],
            models.KeyLength.algo_name == kl["algo_name"]
        ).first()
        if not len_obj:
            len_obj = models.KeyLength(value=kl["value"], algo_name=kl["algo_name"], is_active=True)
            db.add(len_obj)
    db.commit()
    print("Key lengths seeded successfully")

    validity_options = [90, 365, 730, 3650]
    for val in validity_options:
        opt = db.query(models.ValidityOption).filter(models.ValidityOption.value == val).first()
        if not opt:
            opt = models.ValidityOption(value=val, is_active=True)
            db.add(opt)
    db.commit()
    print("Validity options seeded successfully")


if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialization complete.")
