from datetime import datetime
import json
import os
import sys
import pytz
from hdbcli import dbapi
from fastapi import Request

region_display_config = {
    'NA': 'CS North America',
    'APJ': 'CS APJ',
    'EMEAN': 'CS EMEA North',
    'EMEAS': 'CS EMEA South',
    'CHINA': 'CS G.China',
    'LA': 'CS Latin America',
    'MEE': 'CS MEE',
    'GLOBAL': 'Global'
}


def track_endpoint_usage(request: Request):
    datetime_now = datetime.now(pytz.UTC)
    datetime_string = datetime_now.strftime('%Y-%m-%d %H:%M:%S')
    endpoint_name = os.path.relpath(str(request.url), str(request.base_url))
    endpoint_name = endpoint_name.split('?', 1)[0] # remove the parameter string after the api path
    # TODO: Use aicoe-shared-services to access hana and write to table
    # TODO: Store hana schema and table names as constants
    with open('secrets/sapit-core-dev-hana-cloud.json', 'r') as f:
        hana_secrets = json.load(f)
    hana_client = dbapi.connect(
        address=hana_secrets['host'],
        port=hana_secrets['port'],
        user=hana_secrets['user'],
        password=hana_secrets['password'],
        charset='utf-8',
        use_unicode=True,
        encrypt="true",
        sslCryptoProvider="openssl" if sys.platform in ["linux", "darwin", "aix"] else "mscrypto",
        sslTrustStore=hana_secrets["certificate"],
    )
    hana_cursor = hana_client.cursor()
    # TODO: Get Region L1 programmatically for instance ID
    region = os.getenv('REGION')
    if region:
        instance_id = region_display_config[region]
    else:
        instance_id = 'Global'
    hana_cursor.execute(f"""INSERT INTO "XDC_DEV"."RISE_APP_USAGE" VALUES('{datetime_string}', '{instance_id}', '{endpoint_name}') """)
