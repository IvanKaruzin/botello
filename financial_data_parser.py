import requests
import time
from datetime import datetime

class FinancialDataParser:
    def __init__(self):
        self.session = requests.Session()
    
    def get_all_data(self):
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'usd_rub': self.get_usd_rub(),
                'moex_index': self.get_moex_index(),
                'btc_usd': self.get_btc_price(),
            }
            return data
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return None
    
    def get_usd_rub(self):
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = self.session.get(url, timeout=10)
        data = response.json()
        return data['Valute']['USD']['Value']
    
    def get_moex_index(self):
        url = "https://iss.moex.com/iss/engines/stock/markets/index/boards/SNDX/securities.json"
        response = self.session.get(url, timeout=10)
        data = response.json()
        
        for security in data['securities']['data']:
            if security[0] == 'IMOEX':
                return security[3]
        return None
    
    def get_btc_price(self):
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = self.session.get(url, timeout=10)
        data = response.json()
        return float(data['price'])
    
# Использование
#if __name__ == "__main__":
#    parser = FinancialDataParser()
#    data = parser.get_all_data()
#    print(json.dumps(data, indent=2, ensure_ascii=False))