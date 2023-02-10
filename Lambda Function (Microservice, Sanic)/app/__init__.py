from sanic import Sanic
from sanic_cors import CORS
from mangum import Mangum
import os
from dotenv import load_dotenv
load_dotenv()

app = Sanic("UserDashboardService")
CORS(app, resources={r"*": {"origins": "*"}})

# Add Controller
from app.api import Dashboard, AccountReporting
app.add_route(Dashboard.as_view(), "/user-dashboard")
app.add_route(AccountReporting.as_view(), "/user-dashboard/account-reporting")
# /Add Controller

handler = Mangum(app)