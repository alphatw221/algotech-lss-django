from . import _easy_store, service, lib

def excute(command, credential, *args, **kwargs):
    return getattr(_easy_store,command)(credential, *args, **kwargs)


