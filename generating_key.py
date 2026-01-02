import os
import constants
import datetime
import info_for_signature
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization

def create_subject() -> x509.Name:
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, info_for_signature.COUNTRY_NAME),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, info_for_signature.STATE),
        x509.NameAttribute(NameOID.LOCALITY_NAME, info_for_signature.LOCAL_NAME),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, info_for_signature.ORGANIZATION),
        x509.NameAttribute(NameOID.COMMON_NAME, info_for_signature.COMMON_NAME)
    ])

    return subject

def create_prive_key() -> rsa.RSAPrivateKey:
    private_key = rsa.generate_private_key(
        public_exponent=info_for_signature.PUBLIC_EXPONENT,
        key_size=info_for_signature.KEY_SIZE
    )

    return private_key

def create_certificate(subject : x509.Name, issuer : x509.Name, private_key : rsa.RSAPrivateKey, public_key : rsa.RSAPublicKey) -> x509.Certificate:
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=info_for_signature.AMOUNT_OF_DAYS))
        .add_extension(
            x509.SubjectAlternativeName([x509.DNSName(constants.SERVER_HOST_NAME)]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )
    
    return cert

def create_key_and_certificate() -> None:
    private_key = create_prive_key()

    public_key = private_key.public_key()

    subject = issuer = create_subject()

    with open(info_for_signature.SERVER_KEY_NAME_PRIVATE, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open(info_for_signature.SERVER_KEY_NAME_PUBLIC, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    cert = create_certificate(subject, issuer, private_key, public_key)

    with open(info_for_signature.SERVER_CERT_NAME, "wb") as file:
        file.write(cert.public_bytes(serialization.Encoding.PEM))

def files_are_init() -> bool:
    return (info_for_signature.SERVER_CERT_NAME in os.listdir() 
            and info_for_signature.SERVER_KEY_NAME_PUBLIC in os.listdir()
            and info_for_signature.SERVER_KEY_NAME_PRIVATE in os.listdir())