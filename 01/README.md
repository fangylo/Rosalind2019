#### Bee Population

Suppose that at the 𝑖-th day the amount of bees is 𝑛𝑖 kilograms then on the next day the number of bees can be calculated by the following rule:
𝑛𝑖+1=𝑎⋅𝑛𝑖−𝑏⋅𝑛2𝑖

What is the size of the population if he grows it indefinitely?

##### Input format
The first line of the input contains one integer 𝑇 (1≤𝑇≤50)− the number of test cases.

Each of the next 𝑇 lines contains a description of a test case. It consists of three real numbers with no more than three digits after the decimal point 𝑛1, 𝑎 and 𝑏 − the size of the initial generation and the trend constants (0≤𝑛1≤10, 0≤𝑎,𝑏≤3).

##### Output format
The 𝑖-th line of the output should contain the limit (in the mathematical sense) of the population size in kilograms in the 𝑖-th test. If there is no limit output "−1".

Your answer will be considered correct if its absolute or relative error doesn't exceed 10−4.