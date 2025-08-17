from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,       # số vòng lặp
    memory_cost=65536, # 64 MB RAM
    parallelism=2,     # số CPU threads
    hash_len=32,       # độ dài hash
    salt_len=16        # độ dài salt
)

def HashArgon2(password: str) -> str:
    return ph.hash(password)

def VerifyArgon2(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except Exception:
        return False
