from mpl_interactions.controller import Controls


def test_eager_register():
    zoop = []

    def cb(**kwargs):
        zoop.append(1)

    ctrls = Controls(beep=(0, 1), boop=(0, 1))
    ctrls.register_callback(cb, None, eager=True)
    assert len(zoop) == 1

    ctrls = Controls(beep=(0, 1), boop=(0, 1))
    ctrls.register_callback(cb, "beep", eager=False)
    assert len(zoop) == 1

    ctrls.controls["beep"].set_val(0.5)
    assert len(zoop) == 2

    ctrls.controls["boop"].set_val(0.5)
    assert len(zoop) == 2
