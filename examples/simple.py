from jotting import book, read

stream = read.Stream()
book.edit(writer=stream)


@book.mark
def multiply(x, y):
  z = 0
  for i in range(y):
    z = add(z, x)
  return z


@book.mark
def add(x, y):
  return x + y


value = multiply(2, 2)
