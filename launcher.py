# launcher.py
import subprocess
import sys

print("🏁 Starte Parsing...")
subprocess.run([sys.executable, "-m", "scraper.main"], check=True)

print("🏁 Starte Processing...")
subprocess.run([sys.executable, "-m", "scraper.processor.processor"], check=True)

print("✅ Alles abgeschlossen!")
