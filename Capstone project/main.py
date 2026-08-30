from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
import os
import logging
import numpy as np
from pathlib import Path

from src.utils.data_fetcher import DataFetcher
from src.models.predictor import TimeSeriesPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)
os.makedirs(STATIC_DIR / "css", exist_ok=True)
os.makedirs(STATIC_DIR / "js", exist_ok=True)

fetcher = DataFetcher()
predictor = TimeSeriesPredictor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Stock Analytics Dashboard API")
    yield
    logger.info("Shutting down Stock Analytics Dashboard API")

app = FastAPI(
    title="Stock Market Trend Prediction & Financial Analytics Dashboard",
    description="AI-powered stock market analysis with time series forecasting",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_file = TEMPLATES_DIR / "index.html"
    if html_file.exists():
        return html_file.read_text(encoding='utf-8')
    return HTMLResponse(content="<h1>Dashboard not found. Please ensure templates/index.html exists.</h1>", status_code=404)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Stock Analytics API is running"}

@app.get("/api/stock/{symbol}/data")
async def get_stock_data(symbol: str, period: str = "1y", interval: str = "1d"):
    try:
        df = fetcher.get_stock_data(symbol.upper(), period=period, interval=interval)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        df_with_indicators = fetcher.calculate_technical_indicators(df)
        data = df_with_indicators.replace({np.nan: None}).to_dict(orient='records')
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        logger.error(f"Error in get_stock_data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    try:
        info = fetcher.get_stock_info(symbol.upper())
        if info is None:
            raise HTTPException(status_code=404, detail=f"No info found for symbol {symbol}")
        return info
    except Exception as e:
        logger.error(f"Error in get_stock_info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}/predictions")
async def get_predictions(symbol: str, forecast_days: int = 30):
    try:
        df = fetcher.get_stock_data(symbol.upper(), period="1y")
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        df_with_indicators = fetcher.calculate_technical_indicators(df)
        summary = predictor.get_prediction_summary(df_with_indicators)
        return {
            "symbol": symbol.upper(),
            "forecast_days": forecast_days,
            "analysis": summary
        }
    except Exception as e:
        logger.error(f"Error in get_predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market/indices")
async def get_market_indices():
    try:
        indices = fetcher.get_market_indices()
        return {"indices": indices}
    except Exception as e:
        logger.error(f"Error in get_market_indices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stock/{symbol}/signals")
async def get_trading_signals(symbol: str):
    try:
        df = fetcher.get_stock_data(symbol.upper(), period="3mo")
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        df_with_indicators = fetcher.calculate_technical_indicators(df)
        signals = predictor.generate_signals(df_with_indicators)
        sr = predictor.calculate_support_resistance(df_with_indicators)
        vol = predictor.calculate_volatility(df_with_indicators)
        trend = predictor.detect_trend(df_with_indicators)
        return {
            "symbol": symbol.upper(),
            "signals": signals,
            "support_resistance": sr,
            "volatility": vol,
            "trend": trend
        }
    except Exception as e:
        logger.error(f"Error in get_trading_signals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
