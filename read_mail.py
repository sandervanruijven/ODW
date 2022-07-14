import win32com.client
import datetime
import os

# Variable date of today
today = datetime.datetime.today().strftime('%d-%m-%Y')

# Source: https://towardsdatascience.com/automatic-download-email-attachment-with-python-4aa59bc66c25
# Source: https://geekflare.com/how-to-run-python-scripts/

# Set up connection to outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

inbox = outlook.GetDefaultFolder(6)

"""
The index of the folders in Outlook":
3 Deleted Items
4 Outbox 
5 Sent Items
6 Inbox
16 Drafts
"""

# For sub folder, add <.folder("your folder name")>
inbox = outlook.GetDefaultFolder(6).folders("test")

messages = inbox.Items
message = messages.GetFirst()
today_date = str(datetime.date.today())

# Access to the email in the inbox
messages = inbox.Items
# Get the last email
message = messages.GetLast()
# To loop through the email in the inbox
attachments = message.Attachments

# Directory
directory = f"MTM logfiles {today}"
# Parent directory path
parent_dir = 'C:/Users/svanruijven/PycharmProjects/ODW/data/source/'
# Path
path = os.path.join(parent_dir, directory)


def create_folder_if_not_exists(path):
    """
    Create a new folder if it doesn't exists
    """
    os.makedirs(path, exist_ok=True)
    print(f'Folder {path} created')


def save_mail_attachments():
    """
    Sava all email attachments in the new folder
    """
    for i in range(1,4):
        attachment = attachments.Item(i)
        # The name of attachment file
        attachment_name = str(attachment).lower()
        attachment.SaveASFile(path + '\\' + attachment_name)


def main():
    """
    Main function called inside the execute.py script
    """
    print("[Read_mail] Start")
    print("[Read_mail] Creating new folder")
    create_folder_if_not_exists(path)
    print(f"[Read_mail] Saving attachments from {message.subject}")
    save_mail_attachments()
    print("[Read_mail] End")