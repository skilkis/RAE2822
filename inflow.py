from math import sqrt

gamma = 1.4
mach = 0.729
t_total = 291.15
t_ratio = 1 + (((gamma - 1) / 2.) * mach ** 2)
R = 287.05
t_static = t_total / t_ratio

Re = 1e6 * 6


p_total = 101325
p_ratio = (1 + (((gamma - 1) / 2.) * mach**2))**(gamma / (gamma - 1))
p_static = p_total / (1 + (((gamma - 1) / 2.) * mach**2))**(gamma / (gamma - 1))

rho = p_static / (R * t_static)
a = sqrt(gamma * R * t_static)
V = a * mach

S = 110.4
C1 = 1.458 * 1e-6


def sutherland():
    return (C1 * t_static**(3./2.)) / (t_static + S)


mu = sutherland()

c = (Re * mu) / (rho * V)
print(c)
