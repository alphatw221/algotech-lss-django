import lib

def getparams(request, params: tuple, with_user=True, seller=True):
    ret = []
    if with_user:
        if seller:
            if not request.user.api_users.filter(type='user').exists():
                raise lib.error_handle.error.api_error.ApiVerifyError('util.no_api_user_found')
            ret = [request.user.api_users.get(type='user')]
        else:
            if not request.user.api_users.filter(type='customer').exists():
                raise lib.error_handle.error.api_error.ApiVerifyError('util.no_api_user_found')
            ret = [request.user.api_users.get(type='customer')]
    for param in params:
        ret.append(request.query_params.get(param, None))
    return ret

def getdata(request, data: tuple, required=False):
    ret = []
    if required:
        for d in data:
            if type(request.data.get(d)) not in [ bool, int, float] and not request.data.get(d):
                raise lib.error_handle.error.api_error.ApiVerifyError(f"{d} is required")
            ret.append(request.data.get(d))
        return ret

    return [request.data.get(d, None) for d in data]

def getproperties(obj, properties: tuple, nest_property:None):
    if nest_property:
        return [obj.get(property,{}).get(nest_property) for property in properties]

    return [obj.get(property) for property in properties]
