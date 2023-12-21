import pyo
print("host APIs: ", pyo.pa_list_host_apis())
print("all devices: ", pyo.pa_list_devices())
print("default input: ", pyo.pa_get_default_input())
print("default output: ", pyo.pa_get_default_output())
print("output devices: ", pyo.pa_get_output_devices())
# print(pyo.pa_get_default_devices_from_host(pyo.host()))
print("All Done")