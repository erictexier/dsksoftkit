import traceback


def connect():
    sg = None
    try:
        import sgtk
        sg = sgtk.util.shotgun.create_sg_connection()
    except Exception as e:
        traceback.print_exc()
    return sg
