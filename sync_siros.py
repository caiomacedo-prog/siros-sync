import json
import requests
from datetime import datetime, timedelta

AIRLINES  = {'TAM', 'LAN', 'LTM', 'LAT', 'GLO', 'GOL', 'AZU'}
SIROS_URL = 'https://sas.anac.gov.br/sas/siros_api/voos'
DAYS_BACK    = 3
DAYS_FORWARD = 2

today = datetime.utcnow()
dates = [today + timedelta(days=i) for i in range(-DAYS_BACK, DAYS_FORWARD + 1)]

cache = []

for d in dates:
    date_key = d.strftime('%d%m%Y')
    try:
        resp = requests.get(
            SIROS_URL,
            params={'dataReferencia': date_key},
            timeout=30,
            headers={'Accept': 'application/json'}
        )
        resp.raise_for_status()
        flights = resp.json()

        # A API pode retornar lista direta ou objeto com chave 'data'
        if isinstance(flights, dict):
            flights = flights.get('data', flights.get('voos', []))
        if not isinstance(flights, list):
            print(f'{date_key}: resposta inesperada — {str(flights)[:200]}')
            continue

        rows = [
            {
                'date_key':    date_key,
                'airline':     f.get('sg_empresa_icao', ''),
                'flight':      f.get('nr_voo', ''),
                'origin':      f.get('sg_icao_origem', ''),
                'dest':        f.get('sg_icao_destino', ''),
                'dep_utc':     f.get('dt_partida_prevista_utc', ''),
                'arr_utc':     f.get('dt_chegada_prevista_utc', ''),
                'dep_real_utc': f.get('dt_partida_real_utc', ''),
                'arr_real_utc': f.get('dt_chegada_real_utc', ''),
                'status':      f.get('cd_situacao_voo', '')
            }
            for f in flights
            if f.get('sg_empresa_icao') in AIRLINES
        ]

        cache.extend(rows)
        print(f'{date_key}: {len(flights)} totais → {len(rows)} MELI')

    except Exception as e:
        print(f'{date_key}: ERRO — {e}')

with open('siros_cache.json', 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False)

print(f'\nTotal: {len(cache)} voos gravados em siros_cache.json')
