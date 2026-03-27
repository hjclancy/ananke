import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv

load_dotenv()

def login():
    rh.login(
        username=os.getenv("ROBINHOOD_EMAIL"),
        password=os.getenv("ROBINHOOD_PASS"),
        expiresIn=86400,     # 24 hours
        store_session=True   # caches token so MFA isn't required every time
    )
```

Your `.env` file:
```
ROBINHOOD_EMAIL=you@email.com
ROBINHOOD_PASS=yourpassword
