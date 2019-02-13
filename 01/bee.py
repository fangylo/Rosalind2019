from logzero import loglevel, logger


def bee_population_at_day(final_day, starting_population, a, b):
    current_population = starting_population
    for day in range(2, final_day):
        current_population = a * current_population - b * current_population ** 2

        if current_population < 0:
            current_population = 0
            break

        #logger.debug(f'current_population={current_population}')
    return current_population


if __name__ == '__main__':
    loglevel(level=10)
    final_day = 100000

    with open("tests.txt") as f:
        lines = f.readlines()
        lines = [x.strip() for x in lines]
        lines.pop(0) # Get rid of first line
        logger.debug(lines)

    final_limit = []
    for line in lines:
        n1, a, b = [float(x) for x in line.split()]
        logger.debug(f'Current n1={n1}, a={a}, b={b}:')
        if n1 == 0 or a == 0:
            limit = 0
        elif a > 1 and b == 0:
            limit = -1 # no limit
            logger.debug(f'No limit')
        else:
            limit = bee_population_at_day(final_day, n1, a, b)
        logger.debug(limit)
        final_limit.append(limit)

    with open("result.txt", "w") as f:
        for x in final_limit:
            print(x, file = f)



# starting_population = 4.593
# a = 1.357
# b = 1.232

# current_population = starting_population
# for day in range(2, 10):
#   current_population = a * current_population - b * (current_population ** 2)

# with open("tests.txt") as f:
#     lines = f.readlines()
#     lines = [x.strip() for x in lines]
#     lines.pop(0) # Get rid of first line
#     # logger.debug(lines)

# final_limit = []
# for line in lines:
#     n1, a, b = [float(x) for x in line.split()]
#     if a <= b:
#         final_limit.append(0)
#     else:
#         r1 = bee_population_at_day(10000, n1, a, b)
#         r2 = bee_population_at_day(10000000, n1, a, b)
#         final_limit.append((r1, r2))