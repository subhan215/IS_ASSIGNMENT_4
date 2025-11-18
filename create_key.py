# create_key.py (quick one-liner)
from utils import generate_fernet_key
k = generate_fernet_key()
open('fernet.key','wb').write(k)
