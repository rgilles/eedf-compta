from datetime import date

import pytest

from main import (
    as_row,
    BredRow,
    new_accounting_from,
    AccountingRow,
    bred_to_accounting,
)


def test_as_row_basic():

    entry =   ['2025/12/04','','VIREMENT SEPA EMIS  ','-14,25','','M. POUPRY N OU MLLE MOREL                                                     ','REMBOURSEMENT CAMP 2025 AUTOFINANCEMENT ADELE                                ',]
        # ['2025/11/28',2815526,'PRELEVEMENT SEPA    ',-7313.00,None,'EEDF GRAND BIVOUAC                                                            ','GRAND BIVOUAC EEDF PESSAC CESTAS                                             ','FR51ZZZ441024                       SEPA                                     ','0001W                               RCUR                                     ','FA2500290                                                                    ',]

    row = as_row(entry)
    assert row.date == date(2025, 12, 4)
    assert row.operation_ref is None
    assert row.operation_type == 'VIREMENT SEPA EMIS'
    assert row.amount == -14.25
    assert row.comment is None
    assert row.detail1 == 'M. POUPRY N OU MLLE MOREL'
    assert row.detail2 == 'REMBOURSEMENT CAMP 2025 AUTOFINANCEMENT ADELE'


def test_as_row_minimal_entry():

    entry =   ['2025/12/02','8653888','PAIEMENT DE CHEQUE  ','-646.70']

    row = as_row(entry)
    assert row.date == date(2025, 12, 2)
    assert row.operation_ref == '8653888'
    assert row.operation_type == 'PAIEMENT DE CHEQUE'
    assert row.amount == -646.70
    assert row.comment is None
    assert row.detail1 is None
    assert row.detail2 is None



def test_new_accounting_from_expense():
    bread_row = BredRow(
        date(2025, 12, 4),
        None,
        'VIREMENT SEPA EMIS',
        -14.25,
        None,
        'M. POUPRY N OU MLLE MOREL',
        'REMBOURSEMENT CAMP 2025 AUTOFINANCEMENT ADELE'
    )
    accounting_row = new_accounting_from(bread_row)
    assert accounting_row.month == 12
    assert accounting_row.day == 4
    assert accounting_row.piece_number == ''
    assert accounting_row.operation == 'DépensesBRED'
    assert accounting_row.subject is None
    assert accounting_row.description == 'VIREMENT SEPA EMIS | M. POUPRY N OU MLLE MOREL | REMBOURSEMENT CAMP 2025 AUTOFINANCEMENT ADELE'
    assert accounting_row.amount == 14.25


def test_new_accounting_from_income():
    bread_row = BredRow(
        date(2025, 9, 25),
        '9007261',
        'VIREMENT SEPA RECU',
        4783.17,
        None,
        'EEDF GR DINAN',
        'EEDF PESSAC CAM20250923-1'
    )
    accounting_row = new_accounting_from(bread_row)
    assert accounting_row.month == 9
    assert accounting_row.day == 25
    assert accounting_row.piece_number == ''
    assert accounting_row.operation == 'RecettesBRED'
    assert accounting_row.subject is None
    assert accounting_row.description == 'VIREMENT SEPA RECU | EEDF GR DINAN | EEDF PESSAC CAM20250923-1'
    assert accounting_row.amount == 4783.17

def test_new_accounting_from():
    entry =   ['2025/12/04','','CARTE               ','-14.25','','AUTOCORP        LE 17/10/25                                                   ','REF  CB.XXXXX6372                                                            ',]
    accounting_row = bred_to_accounting(42, entry)
    assert accounting_row.month == 12
    assert accounting_row.day == 4
    assert accounting_row.piece_number == '12-04--42'
    assert accounting_row.operation == 'DépensesBRED'
    assert accounting_row.subject == 'Entretiens et réparations'
    assert accounting_row.description == 'CARTE | AUTOCORP LE 17/10/25 | REF CB.XXXXX6372'
    assert accounting_row.amount == 14.25

def test_new_accounting_from_check_payment():
    entry =   ['2025/12/04','8653884','PAIEMENT DE CHEQUE  ','-6.00','','',]
    accounting_row = bred_to_accounting(42, entry)
    assert accounting_row.month == 12
    assert accounting_row.day == 4
    assert accounting_row.piece_number == '12-04--42'
    assert accounting_row.operation == 'DépensesBRED'
    assert accounting_row.subject is None
    assert accounting_row.description == 'PAIEMENT DE CHEQUE'
    assert accounting_row.amount == 6.00

def test_update_piece_number():
    accounting_row = AccountingRow(
        month=1,
        day=1,
        piece_number='',
        operation='DépensesBRED',
        subject=None,
        description='EEDF GR DINAN | EEDF PESSAC CAM20250923-1',
        amount= 123.4
        )
    accounting_row.index_piece_number(1)
    assert accounting_row.piece_number == '01-01--01'
    accounting_row.index_piece_number(2, '.')
    assert accounting_row.piece_number == '01-01.02'


@pytest.mark.parametrize('operation_type, amount, detail1, detail2, expected_operation, expected_subject', [
['CARTE', -12.23, 'CTRE LECLERC    LE 01/11/25', 'REF  CB.XXXXX6372', 'DépensesBRED' ,'Achats denrées alimentaires'],
['CARTE', -12.23,'CASTORAMA LE 20/02/24','REF CB.XXXXX7307', 'DépensesBRED', 'Entretiens et réparations'],
['VIREMENT SEPA EMIS', -12.23, 'REGIE DE L EAU BORDEAUX METROPOLE','464471CCCC FACTURE EEDF PESSAC CESTAS 1939522', 'DépensesBRED', 'Eau, Gaz & Electricité'],
['PAIEMENT DE CHEQUE', -12.23, None,None, 'DépensesBRED', None],
['COTISATION CARTE BUSINESS', -63.60, '(DONT HORS TAXE E.53,00  TVA TAUX 20,00 % E.10,60)',None, 'DépensesBRED', 'Services bancaires & assimilées'],
['PRELEVEMENT SEPA    ', -357.05, 'EDF','EEDF GROUPE PESSAC CESTA REF EDF:1000094826 RUM:++MA8101052445 ? 2025-       ', 'DépensesBRED', 'Eau, Gaz & Electricité'],
['VIREMENT SEPA RECU', 19.00 ,'EEDF SIEGE NATIONAL','DONS PESSAC - CESTAS GIRONDE AU 01/11/2025', 'RecettesBRED', None],
['VIREMENT SEPA RECU', 6709.00, 'HELLOASSOPAY','HELLOASSO', 'RecettesVentilation', None],
['REMISE DEPLACEE CHEQUE', 317.50, 'NR','10907  00000 050825', 'RecettesVentilation', None],
['REMISE DEPLACEE ESPECE', 511.60, '10907  00000            280525','NE000013268241326824', 'RecettesBRED', 'Virement Compte à compte ou caisse'],
])
def test_bred_row_to_subject(operation_type:str, amount:float, detail1:str, detail2:str, expected_operation:str, expected_subject:str):
    accounting_row = new_accounting(operation_type, amount, detail1, detail2)

    assert accounting_row.operation == expected_operation
    assert accounting_row.subject == expected_subject

def new_accounting(operation_type: str|None, amount: float, detail1: str | None, detail2: str | None) -> AccountingRow:
    return new_accounting_from(BredRow(
        date(2025, 12, 4),
        None,
        operation_type,
        amount,
        None,
        detail1,
        detail2
    ))

def test_accounting_as_list():
    accounting_row = AccountingRow(
        month=1,
        day=1,
        piece_number='01-01--01',
        operation='DépensesBRED',
        subject= 'Entretiens et réparations',
        description='EEDF GR DINAN | EEDF PESSAC CAM20250923-1',
        amount= 123.4
    )
    assert accounting_row.as_list() == ["1", "1", "01-01--01", "DépensesBRED", "Entretiens et réparations", "EEDF GR DINAN | EEDF PESSAC CAM20250923-1", "123.4", ]
    assert accounting_row.as_list(decimal_separator=',') == ["1", "1", "01-01--01", "DépensesBRED", "Entretiens et réparations", "EEDF GR DINAN | EEDF PESSAC CAM20250923-1", "123,4",]
