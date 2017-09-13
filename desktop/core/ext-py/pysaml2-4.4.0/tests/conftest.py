import os

#TODO: On my system this function seems to be returning an incorrect location
def pytest_funcarg__xmlsec(request):
    for path in os.environ["PATH"].split(":"):
        fil = os.path.join(path, "xmlsec1")
        if os.access(fil,os.X_OK):
            return fil

    raise Exception("Can't find xmlsec1")
    
def pytest_funcarg__AVA(request):
    return [
        {
            "surName": ["Jeter"],
            "givenName": ["Derek"],
        },
        {
            "surName": ["Howard"],
            "givenName": ["Ryan"],
        },
        {
            "surName": ["Suzuki"],
            "givenName": ["Ischiro"],
        },
        {
            "surName": ["Hedberg"],
            "givenName": ["Roland"],
        },
    ]    
