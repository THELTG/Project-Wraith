from colorama import init, Fore

init(autoreset=True)
translation = {
    '[X]':Fore.RED,
    '[+]':Fore.GREEN,
    '[!]':Fore.BLUE,
    '[-]':Fore.WHITE
}

def decor(text:str)->None:
    try:
        print(translation[text[:3].upper()]+text)
    except:
        print(text)