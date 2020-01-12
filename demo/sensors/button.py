# spikedev libraries
from spikedev.button import ButtonLeft
from spikedev.logging import log_msg

log_msg("start")
btn = ButtonLeft()
btn.wait_for_pressed(5000)
# btn.wait_for_released()
# btn.wait_for_bump()
log_msg("finish")
