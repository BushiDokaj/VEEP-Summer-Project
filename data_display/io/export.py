import csv
import collections
from data_display.utils.string_display import get_strings_from_cache

# use streams pre-emptively in case table sizes get very big
from django.http import StreamingHttpResponse


# Some copy-pasta from the django docs:
class Echo:
    """
        A dummy class used to fit the "writer" interface in csv.
    """
    def write(self, value):
        return value


def export_as_csv(model):
    """
    :param Django model:
    :return: csv file representation of the Django model, wrapped in an HTTP Response
    """
    rows = collections.deque(model.objects.all().values_list())
    rows.appendleft(
        get_strings_from_cache(model._meta.get_fields())
    )
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
                                     content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    return response