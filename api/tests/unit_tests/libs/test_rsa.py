import time

import rsa as pyrsa
from Crypto.PublicKey import RSA
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from libs import gmpy2_pkcs10aep_cipher


def test_gmpy2_pkcs10aep_cipher() -> None:
    rsa_key_pair = pyrsa.newkeys(2048)
    public_key = rsa_key_pair[0].save_pkcs1()
    private_key = rsa_key_pair[1].save_pkcs1()

    public_rsa_key = RSA.import_key(public_key)
    public_cipher_rsa2 = gmpy2_pkcs10aep_cipher.new(public_rsa_key)

    private_rsa_key = RSA.import_key(private_key)
    private_cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_rsa_key)

    raw_text = 'raw_text'
    raw_text_bytes = raw_text.encode()

    # RSA encryption by public key and decryption by private key
    encrypted_by_pub_key = public_cipher_rsa2.encrypt(message=raw_text_bytes)
    decrypted_by_pub_key = private_cipher_rsa.decrypt(encrypted_by_pub_key)
    assert decrypted_by_pub_key == raw_text_bytes

    # RSA encryption and decryption by private key
    encrypted_by_private_key = private_cipher_rsa.encrypt(message=raw_text_bytes)
    decrypted_by_private_key = private_cipher_rsa.decrypt(encrypted_by_private_key)
    assert decrypted_by_private_key == raw_text_bytes

    public_key1 = serialization.load_pem_public_key(public_key)
    private_key1 = serialization.load_pem_private_key(private_key, password=None)
    ciphertext = public_key1.encrypt(
        plaintext=raw_text_bytes,
        padding=padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    decrpted = private_key1.decrypt(ciphertext,
                                    padding.OAEP(
                                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                        algorithm=hashes.SHA256(),
                                        label=None
                                    ))
    assert decrpted == raw_text_bytes


def test_benchmark_2() -> None:
    times = 1000
    raw_text = 'raw_text'
    raw_text_bytes = raw_text.encode()

    rsa_key_pair = pyrsa.newkeys(2048)
    public_key = rsa_key_pair[0].save_pkcs1()
    private_key = rsa_key_pair[1].save_pkcs1()

    print()

    # way1
    public_rsa_key = RSA.import_key(public_key)
    public_cipher_rsa = gmpy2_pkcs10aep_cipher.new(public_rsa_key)

    private_rsa_key = RSA.import_key(private_key)
    private_cipher_rsa = gmpy2_pkcs10aep_cipher.new(private_rsa_key)

    start_time1 = time.time()
    for i in range(times):
        encrypted_by_pub_key = public_cipher_rsa.encrypt(message=raw_text_bytes)
        decrypted_by_pub_key = private_cipher_rsa.decrypt(encrypted_by_pub_key)
        assert decrypted_by_pub_key == raw_text_bytes
    print(f'rsa_with_gmpy2 time: {time.time() - start_time1}')

    # way2

    public_key2 = serialization.load_pem_public_key(public_key)
    private_key2 = serialization.load_pem_private_key(private_key, password=None)

    start_time2 = time.time()
    for i in range(times):
        ciphertext = public_key2.encrypt(
            plaintext=raw_text_bytes,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )

        decrpted = private_key2.decrypt(encrypted_by_pub_key,
                                        padding.OAEP(
                                            mgf=padding.MGF1(algorithm=hashes.SHA1()),
                                            algorithm=hashes.SHA1(),
                                            label=None
                                        ))
        assert decrpted == raw_text_bytes

    print(f'ras_with_cryptography time: {time.time() - start_time2}')
