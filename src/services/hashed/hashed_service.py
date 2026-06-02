import bcrypt

class HashedPasswordService:
    
    @classmethod
    def hash_password(cls, password: str) -> bytes:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(8))
    
    @classmethod
    def verify_password(cls, password: str, hashed_password: bytes) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password)