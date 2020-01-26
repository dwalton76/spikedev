# spikedev libraries
from spikedev.button import ButtonCenter, ButtonLeft, ButtonRight
from spikedev.logging import log_msg

log_msg("start")
btn = ButtonLeft()
btn.wait_for_pressed(1000)
# btn.wait_for_released()
# btn.wait_for_bump()
log_msg("finish")
