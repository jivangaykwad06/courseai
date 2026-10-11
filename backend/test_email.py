import os
import smtplib

from dotenv import load_dotenv


load_dotenv()


email = os.getenv("MAIL_USERNAME")
password = os.getenv("MAIL_PASSWORD")


print("Email:", email)
print(
    "Password loaded:",
    bool(password)
)


try:

    print("Connecting...")

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30
    )

    server.set_debuglevel(1)

    print("Connected.")

    server.ehlo()

    print("Starting TLS...")

    server.starttls()

    print("TLS successful.")

    server.ehlo()

    print("Logging in...")

    server.login(
        email,
        password
    )

    print("LOGIN SUCCESSFUL!")

    server.quit()


except Exception as error:

    print(
        "\nSMTP TEST ERROR:"
    )

    print(
        repr(error)
    )