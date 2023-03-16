from . import default, shc




points_export_processor_class_map = {"617":shc.SHCPointsExportProcessor} #temp

def get_points_export_processor_class(user_subscription):
    return points_export_processor_class_map.get(str(user_subscription.id), default.DefaultPointsExportProcessor)



