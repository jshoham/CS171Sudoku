def nested():
    def sum(a, b):
        return a + b

    a = 1
    print sum(a, 2)


nested()
