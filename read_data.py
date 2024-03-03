import os.path
import math

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class ReadData:
  def __init__(self):
    # If modifying these scopes, delete the file token.json.
    self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    self.spreadsheet_id = "1P8e1KawU9v7YuTZHUYrmXV8m494r9APV_CxzxC6qhDA"
    
    self.creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
      self.creds = Credentials.from_authorized_user_file("token.json", self.scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not self.creds or not self.creds.valid:
      if self.creds and self.creds.expired and self.creds.refresh_token:
        self.creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.scopes
        )
        self.creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(self.creds.to_json())
      
    self.hospitals = {
      "ids": [],
      "names": {},
      "construction_costs": {},
      "lb_beds": {},
      "ub_beds": {},
      "coord_x": {},
      "coord_y": {},
      "built": {}
    }
    self.read_hospital()

    self.equipments = {
      "ids": [],
      "names": {},
      "prices": {},
      "necessary_rates": {},
      "maintenance_freqs": {},
      "maintenance_costs": {}
    }
    self.read_equipment()

    self.staff = {
      "ids": [],
      "teams": {},
      "salaries": {},
      "necessary_rates": {}
    }
    self.read_staff()

    self.consumables = {
      "ids": [],
      "names": {},
      "prices": {},
      "necessary_rates": {}
    }
    self.read_consumable()

  def connect_range(self, range_name):
    try:
      service = build("sheets", "v4", credentials=self.creds)
      # Call the Sheets API
      sheet = service.spreadsheets()
      result = (
          sheet.values()
          .get(spreadsheetId=self.spreadsheet_id, range=range_name)
          .execute()
      )
      values = result.get("values", [])
      if not values:
        print("No data found.")
        return
      return values
    except HttpError as err:
      print(err)

  def read_hospital(self):
    values = self.connect_range("Hospital!A2:H")
    for row in values:
      id = int(row[0])
      self.hospitals["ids"].append(id)
      self.hospitals["names"][id] = row[1]
      self.hospitals["construction_costs"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      self.hospitals["lb_beds"][id] = int(row[3])
      self.hospitals["ub_beds"][id] = int(row[4])
      self.hospitals["coord_x"][id] = float(row[5].replace(",", "."))
      self.hospitals["coord_y"][id] = float(row[6].replace(",", "."))
      self.hospitals["built"][id] = row[7] == "Construído"

  def read_equipment(self):
    values = self.connect_range("Equipamento!A2:F")
    for row in values:
      id = int(row[0])
      self.equipments["ids"].append(id)
      self.equipments["names"][id] = row[1]
      self.equipments["prices"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      self.equipments["necessary_rates"][id] = float(row[3])
      self.equipments["maintenance_freqs"][id] = int(row[4])
      self.equipments["maintenance_costs"][id] = float(
        row[5].replace("R$ ", "").replace(".", "").replace(",", "."))

  def read_staff(self):
    values = self.connect_range("Profissional!A2:E")
    for row in values:
      id = int(row[0])
      self.staff["ids"].append(id)
      self.staff["teams"][id] = row[1]
      self.staff["salaries"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      self.staff["necessary_rates"][id] = math.ceil(7*24/int(row[3]))*float(row[4].replace(",", "."))

  def read_consumable(self):
    values = self.connect_range("Insumo!A2:E")
    for row in values:
      id = int(row[0])
      self.consumables["ids"].append(id)
      self.consumables["names"][id] = row[1]
      self.consumables["prices"][id] = float(
        row[2].replace("R$ ", "").replace(".", "").replace(",", "."))
      self.consumables["necessary_rates"][id] = float(row[4])

read_data = ReadData()
