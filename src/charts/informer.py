from datetime import datetime


def informer(dir_name, **kwargs):

    file = open(f"./{dir_name}/!info!.txt", "w")
    file.write("~~~~~~EXPERIMENT INFO~~~~~~ \n\nDate of experiment: " + datetime.now().strftime("%H:%M:%S %d.%m.%Y") + "\n\n")
    for variable in kwargs:
        file.write(f"{variable}".ljust(25, " ") + str(kwargs[variable]) + "\n")

    file.close()

if __name__ == "__main__":
    informer("test", x = 5, abc = 10, wart = "mala", ble_ble = 10000000, myszka_miki_gra_w_guziki = "kaczor donald pije sok")