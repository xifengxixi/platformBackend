from testcases.models import Testcases


def get_testcases_by_interface_ids(id_list):
    """
    通过接口id获取用例
    :param id_list:
    :return:
    """
    one_list = []
    for interface_id in id_list:
        testcases_qs = Testcases.objects.values_list('id', flat=True).filter(interface_id=interface_id, is_delete=False)
        one_list.extend(list(testcases_qs))
    return one_list