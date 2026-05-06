Zmanim Pro

Automatische Zmanim API voor Raspberry Pi met auto-updates via GitHub.


Features

🌍 City-based Zmanim API

🔄 Auto-update elke 10 min, inclusief dependencies en service restart

📄 Versienummer in version.txt, log in update.log

🪵 Geen handmatig onderhoud nodig na installatie

Installatie

curl -s https://raw.githubusercontent.com/senmdaniel/zmanim-pro/main/install.sh | bash

API

/status → info over actieve stad en feestdagen

/zmanim → halachische tijden en Jom Tov info

/health → health check

Bestanden

zmanim-pro/

├── app/ (code)

├── data/ (json files per city)

├── config/ (settings)

├── update.sh

├── install.sh

├── requirements.txt

├── version.txt

├── update.log

Multi-device support
Elke Pi kan dezelfde repo gebruiken, geen extra configuratie nodig


in de ssh check for logs:        cat /home/mjd/zmanim-pro/update.log
