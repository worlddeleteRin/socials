from config import settings
from pydantic import BaseModel
from apps.sms.smsc import SMSCProvider 

smsc_provider: SMSCProvider = SMSCProvider(
    smsc_login = settings.smsc_login,
    smsc_password = settings.smsc_password
)

class AuthenticationProvider(BaseModel):
    sms_otp_provider = smsc_provider 
    call_otp_provider = smsc_provider 

    def send_call_otp(self, 
        phone: str,
        is_testing: bool = False,
    ) -> tuple[bool, str | None]:
        if is_testing:
            return True, "1234"
        is_success, code = self.call_otp_provider.smsc_send_call_otp(
            phone = phone 
        )
        return is_success, code 

