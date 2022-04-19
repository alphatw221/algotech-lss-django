from api.utils.error_handle.error.api_error import ApiVerifyError


def getparams(request, params: tuple, with_user=True, seller=True):
    ret = []
    print(request.user)
    if with_user:
        if seller:
            if not request.user.api_users.filter(type='user').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='user')]
        else:
            if not request.user.api_users.filter(type='customer').exists():
                raise ApiVerifyError('no api_user found')
            ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param, None))
    return ret


def getdata(request, data: tuple, required=False):
    ret = []
    if required:
        for d in data:
            if not request.data.get(d):
                raise ApiVerifyError(f"{d} is required")
            ret.append(request.data.get(d))
        return ret

    return [request.data.get(d, None) for d in data]
