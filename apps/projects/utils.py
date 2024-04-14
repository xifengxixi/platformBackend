import re
from django.db.models import Count
from interfaces.models import Interfaces
from testsuits.models import Testsuits


def get_count_by_project(datas):
    datas_list = []
    for item in datas:
        # 转换时间格式，可用切片、正则、datetime库等
        # settings中设置了时间格式后就不需要处理了
        # match = re.search(r'(.*)T(.*)\..*?', item['create_time'])
        # item['create_time'] = f'{match.group(1)} {match.group(2)}'

        project_id = item['id']
        # Interfaces.objects.filter(project_id=project_id, is_delete=False).count()
        # 使用interfaces_testcases_objs.query可以在调试的时候查看sql
        interfaces_testcases_objs = Interfaces.objects.values('id').annotate(testcases=Count('testcases')).\
            filter(project_id=project_id, is_delete=False)
        interfaces_count = interfaces_testcases_objs.count()
        testcases_count = 0
        for one_dict in interfaces_testcases_objs:
            testcases_count += one_dict['testcases']

        interfaces_configrures_objs = Interfaces.objects.values('id').annotate(configrures=Count('configrures')). \
            filter(project_id=project_id, is_delete=False)
        configrures_count = 0
        for one_dict in interfaces_configrures_objs:
            configrures_count += one_dict['configrures']

        testsuits_count = Testsuits.objects.filter(project_id=project_id, is_delete=False).count()

        item.update({
            'interfaces': interfaces_count,
            'testcases': testcases_count,
            'configrures': configrures_count,
            'testsuits': testsuits_count
        })
        datas_list.append(item)
    return datas_list