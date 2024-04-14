from testcases.models import Testcases
from configures.models import Configures


def get_count_by_interface(datas):

    for item in datas:
        interface_id = item['id']

        testcases_count = Testcases.objects.filter(interface_id=interface_id, is_delete=False).count()
        configures_count = Configures.objects.filter(interface_id=interface_id, is_delete=False).count()

        item.update({
            'testcases': testcases_count,
            'configures': configures_count,
        })

    return datas