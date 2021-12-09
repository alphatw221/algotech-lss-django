from dataclasses import dataclass

@dataclass 
class MailInfo:
    recipient: str
    subject: str
    content: str

