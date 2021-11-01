def calculate_sample_variance(numbers: list) -> float:
    """ Calculate the sample variance """
    n = len(numbers)
    x_bar = sum(numbers) / n
    sample_variance = sum(map(lambda x: (x - x_bar) ** 2, numbers)) / (n - 1)
    return sample_variance


print(
    f"Sample variance of the set [1, 1, 1, 1, 1]: {calculate_sample_variance([1, 1, 1, 1, 1])}"
)
print(
    f"Sample variance of the set [1, 2, 3, 4, 5]: {calculate_sample_variance([1, 2, 3, 4, 5])}"
)
