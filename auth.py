from passlib.context import CryptContext

# Create a CryptContext instance, specifying the hashing scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """
    Hashes a plain text password.
    Bcrypt has a 72-byte limit, so we truncate the password to ensure it works.
    """
    # Truncate the password to its first 72 characters before hashing.
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str):
    """
    Compares a plain-text password with a hashed password.
    We must truncate the plain password the same way before verifying.
    """
    # Truncate the plain password to its first 72 characters before verifying.
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)