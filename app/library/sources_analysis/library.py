import socket
import ssl
import whois
import OpenSSL

from typing import List
from urllib.parse import urlparse
from datetime import datetime

from tld import get_tld


def get_url_certificate_expiration_date(hostname: str, port: int = 443) -> datetime:
    """
    Возвращает дату истечения срока действия сертификата домена

    Args:
        hostname: доменное имя
        port (optional): порт

    Returns:
        Дата истечения срока действия сертификата домена
    """
    context = ssl.SSLContext()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            certificate = ssock.getpeercert(True)
            cert = ssl.DER_cert_to_PEM_cert(certificate)
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, str.encode(cert))
            cert_expires = datetime.strptime(x509.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%S%z')
            return cert_expires


def get_url_information(url: str) -> dict:
    """
        Возвращает информацию о URL

        Args:
            url: доменное имя

        Returns:
            Информация о URL, которую удастся собрать (дата создания, владелец домена, страна итд)
    """
    return whois.whois(url)


def get_ip_by_url(url: str) -> str:
    """
        Возвращает IP которому соответствует URL

        Args:
            url: доменное имя

        Returns:
            IP которому соответствует url
    """

    return socket.gethostbyname(url)


def urls_are_same(domain_one: str, domain_two: str) -> bool:
    """
    Проверяет, совпадают ли URL
    """
    domain_one = domain_one.replace('https://', '').replace('http://', '')
    domain_two = domain_two.replace('https://', '').replace('http://', '')

    if domain_one.startswith('*.'):
        domain_one = domain_one.replace('*.', '')

    if domain_two.startswith('*.'):
        domain_two = domain_two.replace('*.', '')

    domain_one = 'http://' + domain_one
    domain_two = 'http://' + domain_two

    domain_one = get_tld(domain_one, as_object=True)
    domain_two = get_tld(domain_two, as_object=True)

    if domain_one.fld != domain_two.fld or domain_one.tld != domain_two.tld:
        return False

    return True


if __name__ == '__main__':
    pass