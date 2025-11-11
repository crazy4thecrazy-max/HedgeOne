import datetime

#-----FLYER SETUP -------
REDIRECT_URI = "https://127.0.0.1/"
CLIENT_ID = "CV26HLO9JI-100"
SECRET_KEY = "DST9UGHTX7"
GRANT_TYPE = "authorization_code"       # always has to be authorization code
RESPONSE_TYPE = "code"                  # always has to be code
STATE = "sample"
AUTH_CODE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJDVjI2SExPOUpJIiwidXVpZCI6ImEwYmQzYjk5ZGU3NDQ4Yjk4NDYzZjE0ZDJlZGJmYzZkIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IkZBQzYyMzQ0Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiM2I2ZTI3Y2ZjYzkzMTRkZTRkMGFhOWFiYWVhZGIyNDY1OTkyNmEwOTIxMjk5YmJjYjhjMDY0ZWMiLCJpc0RkcGlFbmFibGVkIjoiTiIsImlzTXRmRW5hYmxlZCI6Ik4iLCJhdWQiOiJbXCJkOjFcIixcImQ6MlwiLFwieDowXCIsXCJ4OjFcIixcIng6MlwiXSIsImV4cCI6MTc2Mjg2Nzc3MiwiaWF0IjoxNzYyODM3NzcyLCJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJuYmYiOjE3NjI4Mzc3NzIsInN1YiI6ImF1dGhfY29kZSJ9.zNVAp8q2kvrhJ_jPSk4QB6_uQ1mbjNy8bNIx4ObyRO0"
def get_logger(module):
    return lambda *args, **kwargs: print(f"[{datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S.%f')}] | {module} |", flush=True, *args, **kwargs)


 
"""
import datetime

logger = get_logger("Crawler")

logger("Starting crawl...")
logger("Fetching URL:", "https://example.com")

OUTPUT:
[2025:08:15 12:30:45.123456] | Crawler | Starting crawl...
[2025:08:15 12:30:45.234567] | Crawler | Fetching URL: https://example.com


WHY USE IT?

Makes logs consistent (always includes time and module).
Easier to debug when multiple modules are printing at the same time.
Works just like print, so you don’t lose flexibility.
"""