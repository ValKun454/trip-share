# обновить код (по желанию)
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TripShare\trip-share-1\scripts\pull.ps1"

# поднять бэкенд + фронтенд; откроет браузер после старта
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\TripShare\trip-share-1\scripts\dev.ps1" -OpenBrowser