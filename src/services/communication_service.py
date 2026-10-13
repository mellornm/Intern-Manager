"""
Service for handling external communication actions like WhatsApp and Email.
"""

import re
import urllib.parse
import webbrowser


class CommunicationService:
    """
    Handles external communication protocols by formatting URLs
    and optionally launching system applications for messaging and email.
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

    def get_whatsapp_url(self, phone: str, message: str = "") -> str:
        """
        Builds a WhatsApp (wa.me) URL with optional message.

        Args:
            phone (str): The recipient's phone number.
            message (str): Optional initial message to send.

        Returns:
            str: Formatted wa.me URL.
        """
        formatted_phone = self.format_whatsapp_number(phone)
        if not formatted_phone:
            return ""

        url_str = f"https://wa.me/{formatted_phone}"
        if message:
            url_str += f"?text={urllib.parse.quote(message)}"
        return url_str

    def open_whatsapp(self, phone: str, message: str = ""):
        """
        Opens WhatsApp web/desktop with a pre-filled message for the given number.

        Args:
            phone (str): The intern's phone number.
            message (str): Optional initial message to send.
        """
        url_str = self.get_whatsapp_url(phone, message)
        if url_str:
            try:
                webbrowser.open(url_str)
            except Exception:
                pass

    def get_email_url(self, email: str, subject: str = "", body: str = "") -> str:
        """
        Builds a mailto URL with optional subject and body.

        Args:
            email (str): Recipient's email address.
            subject (str): Email subject.
            body (str): Email body content.

        Returns:
            str: Formatted mailto URL.
        """
        if not email:
            return ""

        mail_url = f"mailto:{email}"
        params = []
        if subject:
            params.append(f"subject={urllib.parse.quote(subject)}")
        if body:
            params.append(f"body={urllib.parse.quote(body)}")

        if params:
            mail_url += "?" + "&".join(params)

        return mail_url

    def open_email(self, email: str, subject: str = "", body: str = ""):
        """
        Opens the system-default email client.

        Args:
            email (str): Recipient's email address.
            subject (str): Email subject.
            body (str): Email body content.
        """
        mail_url = self.get_email_url(email, subject, body)
        if mail_url:
            try:
                webbrowser.open(mail_url)
            except Exception:
                pass
