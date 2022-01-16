from pypozyx import PozyxSerial, get_first_pozyx_serial_port, UWBSettings, SingleRegister, PozyxConstants, NetworkID

from devices import anchors, remote_tags, load_anchors

load_anchors()

# Identyfikacja taga przypiętego do komputera
serial_port = get_first_pozyx_serial_port()
if serial_port is not None:
    pozyx = PozyxSerial(serial_port)
else:
    print("No Pozyx port was found")
    exit(-1)

network_id = NetworkID()
me = pozyx.getNetworkId(network_id)

print("Default UWB Settings:")
uwb_settings = UWBSettings()
pozyx.getUWBSettings(uwb_settings)
print(uwb_settings)

print(f"\nDevice {hex(me)} is connected to network.")

# Identyfikacja urządzeń w sieci
devices = anchors + remote_tags
connected = 1
for d in devices:
    who_am_i = SingleRegister()
    pozyx.getWhoAmI(who_am_i, remote_id=d)
    if who_am_i == 0x43:
        connected += 1
        print(f"Device {hex(d)} is connected to network.")
    else:
        print(f"Device {hex(d)} is not connected!!!")


print(f"{connected}/{len(devices) + 1} devices connected to network.\n")


# Zmiana ustawień
# Domyślne ustawienia CH: 5, bitrate: 110 kbit/s, prf: 64 MHz, plen: 1024 symbols, gain: 11.5 dB
new_settings = {
    "channel": 2,
    "bitrate": PozyxConstants.UWB_BITRATE_110_KBPS,
    "pulse_repetition_frequecy": PozyxConstants.UWB_PRF_16_MHZ,
    "preamble_length": PozyxConstants.UWB_PLEN_2048,
    "gain": 33.0,
}

# Najpierw zmieniamy urządzeniom w sieci, bo po zmianie stracimy z nimi kontakt.
settings_set = 0
for d in devices:
    uwb_settings = UWBSettings(
        channel=new_settings["channel"],
        prf=new_settings["pulse_repetition_frequecy"],
        plen=new_settings["preamble_length"],
        gain_db=new_settings["gain"],
        bitrate=new_settings["bitrate"])
    ret = pozyx.setUWBSettings(uwb_settings, remote_id=d)
    if ret == 1:
        settings_set += 1
        print(f"Settings for device {hex(d)} changed succefully.")
    elif ret == 0:
        print(f"Cannot change settings for device {hex(d)}.")
    else:
        print(f"Timeout for device {hex(d)}.")

# Na końcu zmieniamy ustawienia urządzenia przypiętego do komputera.
uwb_settings = UWBSettings(
    channel=new_settings["channel"],
    prf=new_settings["pulse_repetition_frequecy"],
    plen=new_settings["preamble_length"],
    gain_db=new_settings["gain"],
    bitrate=new_settings["bitrate"]
)
ret = pozyx.setUWBSettings(uwb_settings)
if ret == 1:
    print(f"Settings for device {hex(me)} changed succefully.\n")
elif ret == 0:
    print(f"Cannot change settings for device {hex(me)}.\n")
else:
    print(f"Timeout for device {hex(me)}.\n")

# Testowanie połączenia po zmianie ustawień
connected = 1
for d in devices:
    who_am_i = SingleRegister()
    pozyx.getWhoAmI(who_am_i, remote_id=d)
    if who_am_i == 0x43:
        connected += 1
        print(f"Device {hex(d)} is connected to network.")
    else:
        print(f"Device {hex(d)} is not connected!!!")
print(f"{connected}/{len(devices) + 1} devices connected to network.\n")

# Nowe ustawiania
uwb_settings = UWBSettings()
pozyx.getUWBSettings(uwb_settings)
print("New settings:")
print(uwb_settings)
