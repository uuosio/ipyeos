import sys

from auditwheel.main import main
from auditwheel.policy import _POLICIES as POLICIES

# libjvm is loaded dynamically; do not include it
for p in POLICIES:
    p['lib_whitelist'].append('ipyeos')

if __name__ == "__main__":
    sys.exit(main())
