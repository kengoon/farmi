from jnius import autoclass, cast, JavaException  # noqa
from sjfirebase.jinterface import OnCompleteListener

_listener = None
_REQUEST_CHECK_SETTINGS = 0x2A


def distance_between_locations(point_1, point_2, unit="km"):
    Location = autoclass("android.location.Location")
    location_1 = Location("location1")
    location_1.setLatitude(point_1[0])
    location_1.setLongitude(point_1[1])

    location_2 = Location("location2")
    location_2.setLatitude(point_2[0])
    location_2.setLongitude(point_2[1])
    if unit == "km":
        return location_1.distanceTo(location_2) / 1000
    return location_1.distanceTo(location_2)


def turn_on_gps(on_enabled, on_disabled, recursive=True):
    global _listener
    from kvdroid import activity

    def on_activity_result(request_code, result_code, _):
        if request_code == _REQUEST_CHECK_SETTINGS and result_code == activity.RESULT_OK:
            on_enabled()
        else:
            if recursive:
                turn_on_gps(on_enabled, on_disabled)
            else:
                on_disabled()

    def check_gps(task):
        from kvdroid import activity
        if task.isSuccessful():
            on_enabled()
        else:
            try:
                resolvable = cast(
                    "com.google.android.gms.common.api.ResolvableApiException",
                    task.getException()
                )
                resolvable.startResolutionForResult(activity, _REQUEST_CHECK_SETTINGS)
            except JavaException:
                pass

    if not _listener:  # stop binding multiple times
        from android.activity import bind as activity_bind  # noqa
        activity_bind(on_activity_result=on_activity_result)

    Priority = autoclass("com.google.android.gms.location.Priority")
    location_request = (
        autoclass("com.google.android.gms.location.LocationRequest$Builder")(
            Priority.PRIORITY_HIGH_ACCURACY, 10000
        )
        .setMinUpdateIntervalMillis(5000)
        .build()
    )
    location_settings_request = (
        autoclass("com.google.android.gms.location.LocationSettingsRequest$Builder")()
        .addLocationRequest(location_request)
        .setAlwaysShow(True)
        .build()
    )
    _listener = OnCompleteListener(lambda task: check_gps(task))
    (
        autoclass("com.google.android.gms.location.LocationServices")
        .getSettingsClient(activity)
        .checkLocationSettings(location_settings_request)
        .addOnCompleteListener(_listener)
    )


def is_jnull(obj):
    Objects = autoclass("java.util.Objects")
    return Objects.isNull(obj)


def compress_image(image_path):
    from kvdroid.jclass.android import BitmapFactory, CompressFormat
    from kvdroid.jclass.java import ByteArrayOutputStream

    bitmap = BitmapFactory().decodeFile(image_path)
    baos = ByteArrayOutputStream(instantiate=True)
    bitmap.compress(CompressFormat().JPEG, 17, baos)
    return baos.toByteArray()


def get_bitmap(image_path):
    from kvdroid.jclass.android import BitmapFactory
    return BitmapFactory().decodeFile(image_path)
