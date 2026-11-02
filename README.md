# Accounting EEDF

## Column
- month
- day
- piece number: month-day-sequence => 01-01--01, 01-01--02, 02-10--01, ...
- operation: { DépensesBRED | RecettesBRED } match from the signe of the amount
- subject (objet): match from description if not found => empty
- description: concat bred `detail 1 / detail 2` 
- amount: absolut value from bred `montant` column
- 

### Operation list
#### Debit
- DépensesBRED
- DépensesCaisse
- DépensesVentilation
#### Credit
- RecettesBRED
- RecettesCaisse
- RecettesVentilation
- amortissements
- Achat à amortir (tentes; Voiture; etc)

### Subject

### Description

### Amount

## Bred
Extract from the date:
- month
- day 
