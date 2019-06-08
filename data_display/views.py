from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.staticfiles import finders
from data_display.models import Students, Teams, Projects, NotForProfits
from data_display.utils import string_display
from data_display.forms import QueryTable, SettingsForm

# TODO: There should be a native app context that Django offers. Store everything we store here there instead.
app_context = {'last_table': "", 'pagination_width': 2, 'last_data': [], 'last_headers': [], 'last_sort': '',
               'ui_obj': {'asc': '', 'desc': ''}}
# this will be changed via settings view in the future
RESULTS_PER_PAGE = 25


# Create your views here.
def database_start_page(request):
    # Add string display to our cache
    string_display.cache_display_strings(finders.find('string_conversion.json'), app_context)

    # Check for all the query parameters
    sort_by = request.GET.get('sort')
    page_number = request.GET.get('page')
    if page_number == None:
        page_number=1
    #table = request.GET.get('table') or 'Students'
    table_choice='Students'
    filter_table=''
    filter_status=False

    if request.method == "GET":
        form = QueryTable(request.GET)
        if form.is_valid():
            table_choice = form.cleaned_data['table_choice']
            filter_table = form.cleaned_data['filter_table']
            filter_status=True
    else:
        filter_status=False
        form = QueryTable()

    if sort_by:
        sort_by = toggle_sort(sort_by, app_context)
        data, table_headers = get_objects_by_table_and_sort(table_choice, sort_by)
        app_context['last_data'], app_context['last_headers'] = data, table_headers
    elif filter_status:
        #print(table_choice)
        data, table_headers = get_objects_by_table_and_filter(table_choice, filter_table)
        app_context['last_data'], app_context['last_headers'] = data, table_headers
    elif not page_number or not app_context['last_data']:
        data, table_headers = get_objects_by_table(table_choice)
        page_number = 1
        app_context['last_data'], app_context['last_headers'] = data, table_headers
    else:
        # This is the pagination case, just use the existing data.
        data, table_headers = app_context['last_data'], app_context['last_headers']

    table_headers = string_display.get_strings_from_cache(table_headers, app_context)

    # paginator is 1-based indexing (yikes)
    paginator = Paginator(data, RESULTS_PER_PAGE)
    subset_data = paginator.page(page_number)

    pages = get_pagination_ranges(paginator, int(page_number))
    return render(
        request, 'data_display/database_start_page.html',
        {'data': subset_data, 'table_headers': table_headers, 'pages': pages, 'ui': app_context['ui_obj'], 'form':form}
    )


def display_data(request):
    # table = request.GET.get('tables')
    # filter_table = request.GET.get('filter')

    return render(request, 'data_display/database_start_page.html', {'example': example})


# Should move this to a model-layer module (this is the resource layer)
def get_objects_by_table(table_name):
    return {
        'Students': (Students.objects.values_list(), Students._meta.get_fields()),
        'Teams': (Teams.objects.values_list(), Teams._meta.get_fields()),
        'Projects': (Projects.objects.values_list(), Projects._meta.get_fields()),
        'Not For Profits': (NotForProfits.objects.values_list(), NotForProfits._meta.get_fields())
    }[table_name]

def get_objects_by_table_and_sort(table_name, sort_by):
    return {
        'Students': (Students.objects.order_by(sort_by).values_list(), Students._meta.get_fields()),
        'Teams': (Teams.objects.order_by(sort_by).values_list(), Teams._meta.get_fields()),
        'Projects': (Projects.objects.order_by(sort_by).values_list(), Projects._meta.get_fields()),
        'Not For Profits': (NotForProfits.objects.order_by(sort_by).values_list(), NotForProfits._meta.get_fields())
    }[table_name]

def get_objects_by_table_and_filter(table_name, filter_table):
    index = filter_table.find(',')
    category = filter_table[:index]
    value = filter_table[(index+1):]
    #print(category)
    #print(value)
    if table_name == 'Students':
        if category == 'student_id':
            try:
                return (Students.objects.filter(student_id=int(value)).values_list(), Students._meta.get_fields())
            except:   # wrong input - return the default filter (name), which will be empty in this case
                return (Students.objects.filter(name=value).values_list(), Students._meta.get_fields())
        elif category == 'name':
            return (Students.objects.filter(name=value).values_list(), Students._meta.get_fields())
        elif category == 'email':
            return (Students.objects.filter(email=value).values_list(), Students._meta.get_fields())
        elif category == 'discipline':
            return (Students.objects.filter(discipline=value).values_list(), Students._meta.get_fields())
        elif category == 'year':
            return (Students.objects.filter(year=value).values_list(), Students._meta.get_fields())
        elif category == 'phone':
            try:
                return (Students.objects.filter(phone=int(value)).values_list(), Students._meta.get_fields())
            except:
                return (Students.objects.filter(name=value).values_list(), Students._meta.get_fields())
        elif category == 'interview_offer':
            try:
                return (Students.objects.filter(interview_offer=bool(value)).values_list(), Students._meta.get_fields())
            except:
                return (Students.objects.filter(name=value).values_list(), Students._meta.get_fields())
        else:
            return (Students.objects.filter(project_name=value).values_list(), Students._meta.get_fields())


    elif table_name == 'Teams':
        if category == 'team_name':
            return (Teams.objects.filter(team_name=value).values_list(), Teams._meta.get_fields())
        elif category == 'num_members':
            try:
                return (Teams.objects.filter(num_members=int(value)).values_list(), Teams._meta.get_fields())
            except:   # wrong input - return the default filter (team_name), which will be empty in this case
                return (Teams.objects.filter(team_name=value).values_list(), Teams._meta.get_fields())
        elif category == 'avg_yos':
            try:
                return (Teams.objects.filter(avg_yos=float(value)).values_list(), Teams._meta.get_fields())
            except:
                return (Teams.objects.filter(team_name=value).values_list(), Teams._meta.get_fields())
        else:
            return (Teams.objects.filter(most_common_discipline=value).values_list(), Teams._meta.get_fields())

    elif table_name == 'Projects':
        if category == 'project_name':
            return (Projects.objects.filter(project_name=value).values_list(), Projects._meta.get_fields())
        elif category == 'client_name':
            return (Projects.objects.filter(client_name=value).values_list(), Projects._meta.get_fields())
        elif category == 'completion_rate':
            try:
                return (Projects.objects.filter(completion_rate=float(value)).values_list(), Projects._meta.get_fields())
            except:
                return (Projects.objects.filter(project_name=value).values_list(), Projects._meta.get_fields())
        else:
            return (Projects.objects.filter(project_type=value).values_list(), Projects._meta.get_fields())

    else:
        if category == 'nfp_name':
            return (NotForProfits.objects.filter(nfp_name=value).values_list(), NotForProfits._meta.get_fields())
        elif category == 'years_w_veep':
            try:
                return (NotForProfits.objects.filter(years_w_veep=float(value)).values_list(), NotForProfits._meta.get_fields())
            except:
                return (NotForProfits.objects.filter(nfp_name=value).values_list(), NotForProfits._meta.get_fields())
        elif category == 'num_projects':
            try:
                return (NotForProfits.objects.filter(num_projects=int(value)).values_list(), NotForProfits._meta.get_fields())
            except:
                return (NotForProfits.objects.filter(nfp_name=value).values_list(), NotForProfits._meta.get_fields())
        elif category == 'num_projects_completed':
            try:
                return (NotForProfits.objects.filter(num_projects_completed=int(value)).values_list(), NotForProfits._meta.get_fields())
            except:
                return (NotForProfits.objects.filter(nfp_name=value).values_list(), NotForProfits._meta.get_fields())
        else:
            return (NotForProfits.objects.filter(primary_email=value).values_list(), NotForProfits._meta.get_fields())



def get_pagination_ranges(paginator, curr_page):
    total_pages = paginator.num_pages
    pages = {'left': [], 'right': [], 'current': curr_page}

    if curr_page - 1 > 1:
        pages['left'] = [curr_page - 2, curr_page - 1]
    if total_pages - curr_page > 1:
        pages['right'] = [curr_page + 1, curr_page + 2]

    return pages


def toggle_sort(sort_by, context):
    asc_sort = string_display.get_strings_from_cache([sort_by], context)[0]
    if context['last_sort'] == asc_sort:
        # already sorted this column -- toggle so desc
        desc_sort = '-' + asc_sort
        context['last_sort'] = desc_sort
        context['ui_obj']['desc'] = sort_by
        return desc_sort
    else:
        # first time we sort, or previous was desc (in which case column doesn't match), do nothing
        context['last_sort'] = asc_sort
        context['ui_obj']['asc'] = sort_by
        return asc_sort
