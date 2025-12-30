from app.fetcher import fetch_stock_data, FetchError
import traceback

if __name__ == '__main__':
    try:
        rows = fetch_stock_data('MSFT','5d')
        print('COUNT:', len(rows))
        print(rows[:2])
    except Exception as e:
        traceback.print_exc()
        print('ERROR:', e)
