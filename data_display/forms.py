from django import forms

class QueryTable(forms.Form):
    table_choice = forms.ChoiceField(label="table",
    choices=[('Students','Students'), ('Projects', 'Projects'), ('Teams', 'Teams'), ('Not for Profits', 'Not for Profits')])
    filter_table = forms.CharField(label="filter", max_length=100)

class SettingsForm():
    rows_per_page = forms.ChoiceField(label="rows per page",
    choices=[(10,'10'),(25,'25'),(50,'50'),(100,'100')])
