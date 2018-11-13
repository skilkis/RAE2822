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
    """ Returns the dynamic viscosity computed with Sutherland's Law """
    return (C1 * t_static**(3./2.)) / (t_static + S)


mu = sutherland()

print(mu)
print('Density = {}'.format(rho))
print('Velocity = {}'.format(V))
print('Temperature = {}'.format(t_static))
print('Static Pressure = {}'.format(p_static))
print('Dynamic Pressure = {}'.format(0.5 * rho * V**2))

# V_pres = sqrt((p_total - p_static)/(0.5 * rho))
# print(V_pres)

c = (Re * mu) / (rho * V)
print('Chord Length = {}'.format(c))
# print(c/2.)

sqrt(170.847/rho)


def yplus():
    return


def get_coefficient(force):
    return force / (0.5 * rho * (V**2) * c**2)


print(get_coefficient(3679.2))
