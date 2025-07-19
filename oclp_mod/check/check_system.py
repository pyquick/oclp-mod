import platform
a=platform.release().rstrip(".0")
def check_kdk():
    if(float(a)>=22.0): return False
    return True
def check_ml():
    if(float(a)>=24.0): return False
    return True