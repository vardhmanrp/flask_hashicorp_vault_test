from flask import Flask
import hvac
import os
from traceback import print_exc
import sys
import psycopg2

app = Flask(__name__)
client = None

def vault_token_auth():
    try:
        global client
        client = hvac.Client(
        url=os.environ['VAULT_ADDR'],
        token=os.environ['VAULT_TOKEN'])
        if client.is_authenticated():
            print("Vault loaded with local token")
        else:
            print("client unable to found local token trying to authenticating again")
    except Exception as e:
        print(print_exc())
        sys.exit(1)

def vault_k8s_auth():
    try:
        f = open('/var/run/secrets/kubernetes.io/serviceaccount/token')
        jwt = f.read()
        client.auth_kubernetes(os.environ['K8S_VAULT_ROLE'], jwt)
        if client.is_authenticated():
            os.environ['VAULT_TOKEN'] = client.token
        return client
    except Exception as e:
        print(print_exc())
        return None

@app.route('/load')
def reloadAuth():
    try:
        vault_token_auth()
        # vault_k8s_auth()
        
        return str(client.is_authenticated())
    except Exception as e:
        print(format_exc())
        return "False"

@app.route('/revoke')
def vaultRevoke():
    try:
        os.environ['VAULT_TOKEN']= ""
    except Exception as e:
        print(format_exc())
        return "False"

@app.route('/products')
def getProducts():
    try:
        print("checking login status")
        if client.is_authenticated():
            print("logic success")
        else:
            print("reattempting login")
            vault_token_auth()
        
        
        secret_version_response = client.secrets.database.get_static_credentials(
        name=os.environ['VAULT_DB_ROLE'],mount_point=os.environ['VAULT_DB_MOUNT']
    )
        conn = None
        if not secret_version_response:
            return {"ERROR: Unable to load credentials"}
        conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        user=secret_version_response['data']['username'],
        password=secret_version_response['data']['password'])
        cur = conn.cursor()
        if not conn:
            return {"Error : unable to connect to DB"}

        cur.execute("select * from products")
        products = cur.fetchall()
        cur.close()
        conn.close()
        if not products:
            return {"ERROR: no products found"}
        return products
            
            
    except Exception as e:
        print(print_exc())
        return "False"



@app.route('/database-secret')
def databaseSecret():
    try:
        print("checking login status")
        if client.is_authenticated():
            print("logic success")
        else:
            print("reattempting login")
            vault_token_auth()
        secret_version_response = client.secrets.database.get_static_credentials(
        name=os.environ['VAULT_DB_ROLE'],mount_point=os.environ['VAULT_DB_MOUNT']
    )
        return secret_version_response['data']
            
            
    except Exception as e:
        print(print_exc())
        return "False"

@app.route('/')
def home():
    print("At home page")
    return "Welcome to testing Hashicorp test for secret"


@app.route('/static-secret')
def staticSecret():
    print("checking login status")
    if client.is_authenticated():
        print("logic success")
    else:
        print("reattempting login")
        vault_token_auth()
    secret_version_response = client.secrets.kv.v2.read_secret_version(
    path=os.environ['VAULT_DATA_PATH'],mount_point=os.environ['VAULT_KV_MOUNT_POINT']
    )
    return secret_version_response['data']['data']


vault_token_auth()

if __name__ == "__main__":
    vault_token_auth()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

