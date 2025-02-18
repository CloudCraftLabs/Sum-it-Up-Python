
def login():
    try:
        print("_____LOGGED IN_____")
        return {"status":True}
    except Exception as err:
        print(err)