from make import Make


if __name__ == "__main__":
    make = Make()
    
    try:
        make.make()
    except Exception as e:
        print(e)