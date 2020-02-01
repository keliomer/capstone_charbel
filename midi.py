import mido
import time
from mido import Message
import random
mido.set_backend('mido.backends.rtmidi')


def get_midi_port():
    for port in mido.get_output_names():
        if 'LoopBe' in port:
            return port
    raise ValueError


def construct_random_output(ctl_number):
    value = random.randint(0,127)
    msg = Message('control_change', channel=0, control=ctl_number, value=value)
    print(msg)
    return msg


def construct_midi(msg_type, **kwargs):
    msg = Message(msg_type, **kwargs)

    return msg

def open_port(name):
    output = mido.open_output(name)
    return output

if __name__ == '__main__':
    p = get_midi_port()

    output = open_port(p)

    on_msg = Message('note_on', note=60, channel=12)
    off_msg = Message('note_off', note=60, channel=12)

    while True:
        try:
            output.send(construct_random_output(26))
            output.send(construct_random_output(26))
            output.send(construct_random_output(26))
            output.send(construct_random_output(26))


            time.sleep(0.1)
        except KeyboardInterrupt:
            break

# print(output)