import requests
from pydantic import BaseModel

class SMSCProvider(BaseModel):
    smsc_login: str
    smsc_password: str

    def smsc_send_call_otp(
        self,
        phone: str,
    ) -> tuple[bool, str | None]:
        base_url = "https://smsc.ru/sys/send.php"   
        params = {
            "login": self.smsc_login,
            "psw": self.smsc_password,
            "phones": phone,
            "mes": "code",
            "call": "1",
            "fmt": 3,
        }
        # print('params are', params)
        response: requests.Response = requests.get(base_url, params = params)
        # print('response is', response.json())
        if 'error' in response.json():
            return False, None
        code = response.json()['code']
        # get only 4 last digets of 6 digets code
        code_final = code[2:]
        return True, code_final
