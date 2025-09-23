from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import random

app = Flask(__name__)
CORS(app)

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'API is working!', 'timestamp': datetime.now().isoformat()})

@app.route('/api/mock-stock-data', methods=['GET'])
def get_mock_stock_data():
    """Fallback endpoint with mock data for testing"""
    symbol = request.args.get('symbol', 'AAPL')
    start_date = request.args.get('start_date', '2023-01-01')
    end_date = request.args.get('end_date', '2023-12-31')

    # Generate mock data
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    data = []
    current_price = 150.0  # Starting price
    current_date = start

    while current_date <= end:
        # Add some randomness to make it look realistic
        price_change = random.uniform(-5, 5)
        current_price = max(10, current_price + price_change)  # Minimum price of $10

        data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'open': round(current_price, 2),
            'high': round(current_price + random.uniform(0, 3), 2),
            'low': round(current_price - random.uniform(0, 3), 2),
            'close': round(current_price, 2),
            'volume': random.randint(1000000, 50000000)
        })

        current_date += timedelta(days=1)

        # Skip weekends (simple approximation)
        if current_date.weekday() >= 5:
            current_date += timedelta(days=2)

    return jsonify({
        'symbol': symbol.upper(),
        'data': data[:100]  # Limit to 100 points for demo
    })

@app.route('/api/stock-data', methods=['GET'])
def get_stock_data():
    print(f"get_stock_data")
    try:
        symbol = request.args.get('symbol')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not symbol or not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters: symbol, start_date, end_date'}),400
        
        print(f"Fetching data for {symbol} from {start_date} to {end_date}")
       
        # Try different approaches to get data
        stock = yf.Ticker(symbol)

        # Method 1: Try basic history call
        try:
            hist = stock.history(start=start_date, end=end_date)
            print(f"Method 1 - Retrieved {len(hist)} rows of data")
        except Exception as e:
            print(f"Method 1 failed: {e}")
            hist = pd.DataFrame()

        if hist.empty:
          return jsonify({'error': f'No data found for symbol {symbol}. Yahoo Finance may be experiencing issues. Try /api/mock-stock-data for testing.'}), 404

        
        # Convert to JSON format
        data = []
        for date, row in hist.iterrows():
            try:
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
                })
            except Exception as row_error:
                print(f"Error processing row {date}: {row_error}")
                continue

        print(f"Successfully processed {len(data)} data points")

        return jsonify({
            'symbol': symbol.upper(),
            'data': data
        })
    except Exception as e:
        print(f"Error in get_stock_data: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500
    

# @app.route('/api/stock-data', methods=['GET'])
# def get_stock_data():
#     print(f"get_stock_data")
#     try:
#         symbol = request.args.get('symbol')
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')

#         if not symbol or not start_date or not end_date:
#             return jsonify({'error': 'Missing required parameters: symbol, start_date, end_date'}), 400

#         print(f"Fetching data for {symbol} from {start_date} to {end_date}")
#         Flask.logger.info(f"Fetching data for {symbol} from {start_date} to {end_date}")

    #     # Try different approaches to get data
    #     stock = yf.Ticker(symbol)

    #     # Method 1: Try basic history call
    #     try:
    #         hist = stock.history(start=start_date, end=end_date)
    #         print(f"Method 1 - Retrieved {len(hist)} rows of data")
    #     except Exception as e:
    #         print(f"Method 1 failed: {e}")
    #         hist = pd.DataFrame()

    #     # Method 2: If that fails, try with different parameters
    #     if hist.empty:
    #         try:
    #             hist = stock.history(period="1y", interval="1d")
    #             print(f"Method 2 - Retrieved {len(hist)} rows with 1y period")
    #         except Exception as e:
    #             print(f"Method 2 failed: {e}")

    #     # Method 3: Try shorter period
    #     if hist.empty:
    #         try:
    #             hist = stock.history(period="3mo")
    #             print(f"Method 3 - Retrieved {len(hist)} rows with 3mo period")
    #         except Exception as e:
    #             print(f"Method 3 failed: {e}")

    #     # Method 4: Try to get basic info to verify symbol exists
    #     if hist.empty:
    #         try:
    #             info = stock.info
    #             print(f"Stock info exists for {symbol}: {info.get('longName', 'Unknown')}")
    #             # If info exists but no history, return a helpful message
    #             if info:
    #                 return jsonify({'error': f'Symbol {symbol} exists but historical data is unavailable. Try using /api/mock-stock-data for testing.'}), 404
    #         except Exception as e:
    #             print(f"Method 4 failed: {e}")

    #     if hist.empty:
    #         return jsonify({'error': f'No data found for symbol {symbol}. Yahoo Finance may be experiencing issues. Try /api/mock-stock-data for testing.'}), 404

    #     # Convert to JSON format
    #     data = []
    #     for date, row in hist.iterrows():
    #         try:
    #             data.append({
    #                 'date': date.strftime('%Y-%m-%d'),
    #                 'open': round(float(row['Open']), 2),
    #                 'high': round(float(row['High']), 2),
    #                 'low': round(float(row['Low']), 2),
    #                 'close': round(float(row['Close']), 2),
    #                 'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0
    #             })
    #         except Exception as row_error:
    #             print(f"Error processing row {date}: {row_error}")
    #             continue

    #     print(f"Successfully processed {len(data)} data points")

    #     return jsonify({
    #         'symbol': symbol.upper(),
    #         'data': data
    #     })

    # except Exception as e:
    #     print(f"Error in get_stock_data: {e}")
    #     return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)