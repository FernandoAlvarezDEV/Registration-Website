import os
import sys
from dotenv import load_dotenv

load_dotenv()
from supabase import create_client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Variables SUPABASE_URL o SUPABASE_SERVICE_KEY no existen en el entorno.")
    sys.exit(1)

client = create_client(url, key)

try:
    print("Intentando listar buckets...")
    buckets = client.storage.list_buckets()
    print(f"Buckets encontrados: {[b.name for b in buckets]}")
    
    if "comprobantes" not in [b.name for b in buckets]:
        print("El bucket 'comprobantes' no existe.")
    else:
        print("El bucket 'comprobantes' SI existe y es accesible.")
except Exception as e:
    print(f"Error conectando a Supabase: {e}")
