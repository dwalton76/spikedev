# spikedev libraries
from spikedev.button import ButtonLeft
from spikedev.logging import log_msg

log_msg("start")
btn = ButtonLeft()
btn.wait_for_pressed(5000)
log_msg("finish")
