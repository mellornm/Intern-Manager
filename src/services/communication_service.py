"""
Service for handling external communication actions like WhatsApp and Email.
"""

import re
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl


class CommunicationService:
    """
    Handles external communication protocols by opening system-default 
    applications for messaging and email.
    """

    def format_whatsapp_number(self, phone: str) -> str:
        """
        Formats a phone number to be compatible with WhatsApp (wa.me).
        Removes all non-numeric characters and ensures the DDI 55 (Brazil)
        is present if only 10 or 11 digits are provided.

        Args:
            phone (str): The raw phone number.

        Returns:
            str: The formatted number for wa.me.
        """
        if not phone:
            return ""

        # Remove everything that is not a digit
        digits = re.sub(r"\D", "", phone)

        # If it has 10 or 11 digits, we assume it's a Brazilian number without DDI
        if len(digits) in [10, 11]:
            return f"55{digits}"
        
        return digits

    def open_whatsapp(self, phone: str, message: str = ""):
        """
        Opens WhatsApp web/desktop with a pre-filled message for the given number.

        Args:
            phone (str): The intern's phone number.
            message (str): Optional initial message to send.
        """
        formatted_phone = self.format_whatsapp_number(phone)
        if not formatted_phone:
            return

        url_str = f"https://wa.me/{formatted_phone}"
        if message:
            # QUrl.toPercentEncoding returns QByteArray. 
            # We use .data() to get a buffer (memoryview) and convert to bytes for decoding.
            query_bytes = QUrl.toPercentEncoding(message).data()
            url_str += f"?text={bytes(query_bytes).decode('utf-8')}"

        QDesktopServices.openUrl(QUrl(url_str))

    def open_email(self, email: str, subject: str = "", body: str = ""):
        """
        Opens the system-default email client.

        Args:
            email (str): Recipient's email address.
            subject (str): Email subject.
            body (str): Email body content.
        """
        if not email:
            return

        mail_url = f"mailto:{email}"
        params = []
        if subject:
            # Convert QByteArray data to bytes explicitly to satisfy Pylance and handle memoryview
            subject_bytes = QUrl.toPercentEncoding(subject).data()
            encoded_subject = bytes(subject_bytes).decode('utf-8')
            params.append(f"subject={encoded_subject}")
        if body:
            # Convert QByteArray data to bytes explicitly
            body_bytes = QUrl.toPercentEncoding(body).data()
            encoded_body = bytes(body_bytes).decode('utf-8')
            params.append(f"body={encoded_body}")

        if params:
            mail_url += "?" + "&".join(params)

        QDesktopServices.openUrl(QUrl(mail_url))
