from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db

app = FastAPI(title="KBC Kế Toán API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "KBC Kế Toán API v1.0 - TT133/2016"}


from app.routers import auth_router, accounts, vouchers, reports

app.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(vouchers.router, prefix="/vouchers", tags=["Vouchers"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
