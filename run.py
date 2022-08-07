from flask import Flask
import hvac
import os
from traceback import print_exc
import sys

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

@app.route('/reloadvault')
def reloadAuth():
    try:
        vault_token_auth()
        # vault_k8s_auth()
        
        return str(client.is_authenticated())
    except Exception as e:
        print(format_exc())
        return "False"





@app.route('/')
def hello():
    print("checking login status")
    if client.is_authenticated():
        print("logic success")
    else:
        print("reattempting login")
        vault_token_auth()
    secret_version_response = client.secrets.kv.v2.read_secret_version(
    path=os.environ['VAULT_DATA_PATH'],mount_point='kv2'
    )
    return secret_version_response['data']['data']


vault_token_auth()
#  if __name__ == "__main__":
#    app.run(debug=True)