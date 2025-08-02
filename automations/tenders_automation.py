import pandas as pd
from sodapy import Socrata
from dotenv import load_dotenv
import os
import json

import requests
from datetime import datetime, timedelta

fifteen = (datetime.today() - timedelta(days=15)).strftime('%Y-%m-%d')
endpoint = "https://www.datos.gov.co/resource/p6dx-8zbt.json"

load_dotenv()
api_key = os.getenv("CLIENT_API_KEY_GOV_CO")

client = Socrata("www.datos.gov.co",
                  api_key,
                  username="##",
                  password="##")


query = f"""
SELECT entidad, nombre_del_procedimiento,
    descripci_n_del_procedimiento, fase, fecha_de_ultima_publicaci, precio_base,
    proveedores_invitados, proveedores_con_invitacion, visualizaciones_del,
    proveedores_que_manifestaron, id_estado_del_procedimiento,
    codigo_principal_de_categoria, urlproceso, estado_del_procedimiento, adjudicado,
    estado_resumen, fecha_adjudicacion, fecha_de_publicacion, referencia_del_proceso
WHERE adjudicado = 'No'
AND id_estado_del_procedimiento = '50'
AND fecha_de_publicacion > '{fifteen}'
"""

query_count_total = f"""
SELECT COUNT(*)
WHERE adjudicado = 'No'
AND id_estado_del_procedimiento = '50'
AND fecha_de_publicacion > '{fifteen}'
"""


def fetch_data():
    limit, offset, all_data = 10, 0, []
    
    params_count = {"$query": query_count_total}
    response_count = requests.get(endpoint, params=params_count)
    response_count.raise_for_status()
    
    total_register = response_count.json()
    total_register = int(total_register[0]['COUNT'])

    while offset < total_register:
        params = {"$query": f"{query} LIMIT {limit} OFFSET {offset}"}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        batch = response.json()
        all_data.extend(batch)
        print(f"Fetched {len(batch)} records, total fetched: {len(all_data)}")
        offset += limit

    return {
        "data":pd.DataFrame(all_data).to_dict(orient="records"),
        "total": total_register
    }





