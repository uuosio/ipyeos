with open('./dd/state/shared_memory.bin', 'rb+') as f:
 f.seek(8)
 f.write(b'\x00')
