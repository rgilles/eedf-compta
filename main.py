import math
from dataclasses import dataclass
from pathlib import Path
from datetime import date

import click
import csv

EXPENSE_FOOD = 'Achats denrées alimentaires'
EXPENSE_MAINTENANCE = 'Entretiens et réparations'
EXPENSE_TEACHING = 'Fournitures Educatives & Pédagogiques'
EXPENSE_SERVICE = 'Eau, Gaz & Electricité'
EXPENSE_INSURANCE = "Frais d'assurance"
EXPENSE_BANK = 'Services bancaires & assimilées'
EXPENSE_FUEL = 'Carburants'
EXPENSE_MISSION = 'Déplacements, missions et réception'
EXPENSE_EQUIPMENT = "Fournitures d'entretien, petit équipement, pharmacie"
EXPENSE_RESALE = "Achats pour la revente"
EXPENSE_RENTING = "Locations immobilières"

EXPENSE_TO_SUBJECT = (
    ("REGIE DE L EAU", EXPENSE_SERVICE),
    (" EDF ", EXPENSE_SERVICE),
    ("LECLERC", EXPENSE_FOOD),
    ("AUCHAN", EXPENSE_FOOD),
    ("METRO", EXPENSE_FOOD),
    ("FOURNIL", EXPENSE_FOOD),
    ("FORTIN", EXPENSE_FOOD),
    ("SBN", EXPENSE_FOOD),
    ("4819 GRADIGNAN", EXPENSE_FOOD), # TODO validate
    ("INTERMARCHE", EXPENSE_FOOD),
    ("BIO", EXPENSE_FOOD),
    ("GLACES", EXPENSE_FOOD),
    ("CARREFOUR", EXPENSE_FOOD),
    ("SUPER U", EXPENSE_FOOD),
    ("ATELIER DOUCEUR", EXPENSE_FOOD),
    ("SOGOPE", EXPENSE_FOOD),
    ("RELAY", EXPENSE_FOOD),
    ("KFC", EXPENSE_FOOD),
    ("LIDL", EXPENSE_FOOD),
    ("SELECTA", EXPENSE_FOOD),
    ("PETITE ROTISSER", EXPENSE_FOOD),
    ("CASTORAMA", EXPENSE_MAINTENANCE),
    ("LEROY", EXPENSE_MAINTENANCE),
    ("AUTOCORP", EXPENSE_MAINTENANCE),
    ("FEU VERT", EXPENSE_MAINTENANCE),
    ("AUTO SECURITE", EXPENSE_MAINTENANCE),
    ("BRICOLAGE", EXPENSE_MAINTENANCE),
    ("NORAUTO", EXPENSE_MAINTENANCE),
    ("SMARTY", EXPENSE_MAINTENANCE),
    ("AUTOROUTE", EXPENSE_MISSION),
    ("APRR", EXPENSE_MISSION),
    ("ESCOTA", EXPENSE_MISSION),
    ("HORODATEUR", EXPENSE_MISSION),
    ("PARKING", EXPENSE_MISSION),
    ("BLABLACAR", EXPENSE_MISSION),
    ("CULTURA", EXPENSE_TEACHING),
    ("DECATHLON", EXPENSE_TEACHING),
    ("GIFI", EXPENSE_TEACHING),
    ("LEGO STORE", EXPENSE_TEACHING),
    ("NATURE", EXPENSE_TEACHING),
    ("PHARMACIE", EXPENSE_EQUIPMENT),
    ("DIFFUS'LAINE", EXPENSE_EQUIPMENT),
    ("LE JARDIN", EXPENSE_EQUIPMENT),
    ("BOULANGER", EXPENSE_EQUIPMENT),
    ("ACTION", EXPENSE_EQUIPMENT),
    ("AMAZON", EXPENSE_EQUIPMENT),
    ("TOTAL", EXPENSE_FUEL),
    ("ESSO", EXPENSE_FUEL),
    ("JEFF DE BRUGES", EXPENSE_RESALE),
    ("SCOUTIK", EXPENSE_RESALE),
    ("AIRBNB", EXPENSE_RENTING),
    ("MAIF", EXPENSE_INSURANCE),
    ("AVAST", "Fournitures administratives"),
    ("EASYFLYER", "Publicité, Publications & relations publiques"),
    ("FRAIS DE CARTE", EXPENSE_BANK),
    ("COTISATION CARTE BUSINESS", EXPENSE_BANK),
)


@dataclass
class BredRow:
    date: date
    operation_ref: str | None
    operation_type: str | None
    amount: float
    comment: str | None
    detail1: str | None
    detail2: str | None

@dataclass
class AccountingRow:
    month: int
    day: int
    piece_number: str
    operation: str
    subject: str | None
    description: str | None
    amount: float

    def index_piece_number(self, index: int, separator: str = '--'):
        self.piece_number = f"{self.month:02d}-{self.day:02d}{separator}{index:02d}"
        return self

    def as_list(self, decimal_separator: str | None =None):
        if decimal_separator is not None:
            def amount_to_str(amount: str):
                return str(amount).replace('.', decimal_separator)
        else:
            amount_to_str = str

        return [str(self.month), str(self.day), self.piece_number, self.operation, self.subject, self.description, amount_to_str(self.amount)]

def safe_get(row, index) -> str | None:
    value = row[index].strip() if len(row) > index else ''
    normalized = normalize(value)
    return normalized

def normalize(value: str):
    value = value.strip()
    value  = " ".join(value.split())
    return None if value == '' else value


def as_row(csv_row: list[str|None|float]) -> BredRow:
    operation_date = date.fromisoformat(csv_row[0].replace('/', '-'))
    operation_ref = safe_get(csv_row, 1)
    operation_type = safe_get(csv_row,2)
    amount = float(csv_row[3].replace(',','.'))
    comment = safe_get(csv_row, 4)
    detail1 = safe_get(csv_row, 5)
    detail2 = safe_get(csv_row,6)
    return BredRow(operation_date, operation_ref, operation_type, amount, comment, detail1, detail2)


def new_accounting_from(value: BredRow) -> AccountingRow:
    description = get_description(value)
    if value.amount < 0:
        operation = "DépensesBRED"
        subject = get_subject(description)

    else:
        if "hello" in description.lower() or "REMISE DEPLACEE CHEQUE" in (value.operation_type if value.operation_type is not None else '') :
            operation = "RecettesVentilation"
            subject = None
        elif 'REMISE DEPLACEE ESPECE' in (value.operation_type if value.operation_type is not None else ''):
            operation = "RecettesBRED"
            subject = "Virement Compte à compte ou caisse"
        else:
            operation = "RecettesBRED"
            subject = None

    return AccountingRow(
        month=value.date.month,
        day=value.date.day,
        piece_number='',
        operation=operation,
        subject=subject,
        description=description,
        amount=math.fabs(value.amount)
    )


def get_description(value: BredRow) -> str | None:
    description = value.operation_type
    if value.detail1 is not None:
        description += " | "
        description += value.detail1
    if value.detail2 is not None:
        description += " | "
        description += value.detail2
    return description

def get_subject(description: str|None):
    subject = None
    description = description if description is not None else ""
    for key, value in EXPENSE_TO_SUBJECT:
        if key in description:
            subject = value
            break
    return subject


@click.group("bred")
def bred():
    pass

@bred.command(name='csv')
@click.option('-i','--input-csv', required=True, type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),help='Path to the bread csv file')
@click.option('-s','--start-at', required=False, type=click.INT, default= 1,help='Start piece numbering at this index value.')
def csv_to_accounting(input_csv: Path, start_at: int):
    # read bread csv
    with open(input_csv, 'rt', newline='') as csvfile:
        spawn_reader = csv.reader(csvfile, delimiter=';')
        # skip header
        next(spawn_reader)
        input_rows = [row for row in spawn_reader]
        input_rows.reverse()
        accounting = [bred_to_accounting(index, row) for index, row in enumerate(input_rows, start=start_at)]

    with open("accounting.csv", "w", newline="") as output_file:
        spam_writer = csv.writer(
            output_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_NONNUMERIC
        )
        for row in accounting:
            spam_writer.writerow(row.as_list(decimal_separator=','))

def bred_to_accounting(index: int, row: list[str]) -> AccountingRow:
    return new_accounting_from(as_row(row)).index_piece_number(index)

@bred.command()
@click.option('-i','--input', required=True, type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),help='Path to the bread csv file')
def hello():
    pass


if __name__ == "__main__":
    bred()
