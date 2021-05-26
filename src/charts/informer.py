from datetime import datetime


def informer(dir_name, **kwargs):

    file = open(f"./{dir_name}/!info!.txt", "w")
    file.write("~~~~~~EXPERIMENT INFO~~~~~~ \n\nDate of experiment: " + datetime.now().strftime("%H:%M:%S %d.%m.%Y") + "\n\n")
    for variable in sorted(kwargs):
        file.write(f"{variable}".ljust(25, " ") + str(kwargs[variable]) + "\n")

    file.close()