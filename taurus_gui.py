from taurus.qt.qtgui.panel import TaurusForm, TaurusCommandsForm
from taurus.qt.qtgui.application import TaurusApplication
from taurus.qt.qtgui.taurusgui import TaurusGui
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusGroupBox

# Remember to export TANGO_HOST=localhost:10000
app = TaurusApplication(cmd_line_parser=None, app_name="MyGui")

widget = TaurusGroupBox("Example")
layout = Qt.QVBoxLayout()
widget.setLayout(layout)
widget.model = "my/device/name"

panel = TaurusForm()
props = ["State", "Status", "RampRate"]
model = [f"{widget.model}/%s" % p for p in props]
panel.setModel(model)
layout.addWidget(panel)

panel = TaurusCommandsForm()
panel.setModel(widget.model)
layout.addWidget(panel)


for prefix in ["1", "2", "3", "4"]:
    panel = TaurusForm()
    props = [
        f"RAMP0{prefix}_Current",
        f"RAMP0{prefix}_Enabled",
        f"RAMP0{prefix}_End",
        f"RAMP0{prefix}_Start",
    ]
    model = [f"{widget.model}/%s" % p for p in props]
    panel.setModel(model)
    layout.addWidget(panel)


gui = TaurusGui()
gui.createPanel(widget, "TempController")
gui.show()
app.exec_()
