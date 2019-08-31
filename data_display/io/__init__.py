"""
Contains import/export functions used to get and put data from/into the database.

Imports are from Google Sheets and contain different formats for convenience to the user. Some imports automatically
infer the columns from the Google Sheet based on "closeness" to the columns of an existing table. Currently this is done
through a weighted average of a fuzzy match and edit distance (https://en.wikipedia.org/wiki/Edit_distance),
though future extensions of importscan utilize some form of sentiment analysis with NLP.

Exports can be in a variety of formats, though currently only CSV is supported.

Future work may include transformation of the data prior to import or export into/out of the database.
"""