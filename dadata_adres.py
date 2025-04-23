import json
from dadata import Dadata

def api_address(address):
  token = "28f0c46ebf7a04748add3fc4f2990d2b2b979d44" # Replace with your Dadata token
  secret = "576db248eb70b56c0f1649f1242cddeecabc9d92"
  dadata = Dadata(token, secret)
  try:
      result = dadata.clean("address", address)
      return json.dumps(result, ensure_ascii=False, indent=2)
  except Exception as e:
      print(f"Ошибка при стандартизации адреса '{address}': {e}")
      return None

address = 'москва улица космонавтов 1'
print(api_address(address))