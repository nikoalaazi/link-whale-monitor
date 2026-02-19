# Google Sheets Import Helper

## Автоматический импорт данных в Google Sheets

### Формат данных
Скрипт создаёт файл `link_whale_results.json` с данными в формате:
```json
{
  "timestamp": "2026-02-19T14:30:00",
  "sheet_id": "1mBarEhev9RvXZQrqcU4S5Y8hqA8qXKxPfjhH69Y9AMk",
  "rows": [
    ["2026-02-19T14:30:00", "0x123...", "Binance", "5000", "https://etherscan.io/...", "Verified"]
  ],
  "wallets": [
    {
      "address": "0x123...",
      "exchange": "Binance",
      "amount": "5000",
      "timestamp": "2026-02-19T14:30:00",
      "etherscan_url": "https://etherscan.io/...",
      "verified": true
    }
  ]
}
```

### Способ 1: Импорт вручную (рекомендуется)
1. Откройте: https://docs.google.com/spreadsheets/d/1mBarEhev9RvXZQrqcU4S5Y8hqA8qXKxPfjhH69Y9AMk/edit
2. Файл → Импорт
3. Загрузите файл `/home/ubuntu/.openclaw/workspace/link_whale_results.json`
4. Выберите формат: JSON (если доступен) или текст

### Способ 2: Через Google Apps Script (автоматический)
Добавьте в свою таблицу скрипт Apps Script:
```javascript
function importLinkWhaleData() {
  // URL JSON-файла (через веб-хостинг или API)
  var url = 'your-json-url';
  
  var response = UrlFetchApp.fetch(url);
  var data = JSON.parse(response.getContentText());
  
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  var targetSheet = sheet.getActiveSheet();
  
  // Заголовки
  targetSheet.getRange(1, 1, 1, 6).setValues([[
    "Timestamp", "Wallet Address", "Exchange", "Amount (LINK)", "Etherscan", "Status"
  ]]);
  
  // Данные
  for (var i = 0; i < data.rows.length; i++) {
    targetSheet.getRange(i + 2, 1, 1, 6).setValues([data.rows[i]]);
  }
}
```

### Способ 3: Через Python с библиотеками
Если `gspread` установлена позже:
```python
import gspread
from google.oauth2.service_account import Credentials

scopes = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(
    '/home/ubuntu/.openclaw/google_service_account.json', 
    scopes=scopes
)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
sheet.append_row([timestamp, address, exchange, amount, url, status])
```

### Текущий режим работы
Скрипт сохраняет данные локально. Для полной автоматизации требуется:
- Вариант A: Ручной импорт (сейчас)
- Вариант B: Настроить Apps Script в таблице
- Вариант C: Установить `gspread` в будущем

---
*Последнее обновление: 2026-02-19*