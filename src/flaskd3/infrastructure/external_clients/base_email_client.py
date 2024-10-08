from flaskd3.appcore.core.extensions import external_servers


class BaseEmailClient:
    def send_mail(self, message):
        return external_servers["mail"].send(message)
