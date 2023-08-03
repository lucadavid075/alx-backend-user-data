#!/usr/bin/env python3
"""
Encrypting passwords module.
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Fucntion that hashes a password using bcrypt and
    returns the salted/hashed password as a byte string.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Function that validates if the password
    matches the hashed password
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
