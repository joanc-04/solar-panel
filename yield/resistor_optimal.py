import numpy as np
import matplotlib.pyplot as plt


def readData(filename="data.csv"):
    X_1 = []
    X_2 = []
    P = []
    with open(filename, "r", encoding="utf-8-sig") as file:
        for line in file:
            lineSplit = line.strip().split(",")
            P.append(float(lineSplit[0]))
            X_1.append((float(lineSplit[1]), float(lineSplit[2])))
            X_2.append((float(lineSplit[3]), float(lineSplit[4])))
    return np.array(P), np.array(X_1), np.array(X_2)


P, X_1, X_2 = readData()

index = max(enumerate(P), key=lambda x: x[1])[0]

fig, ax = plt.subplots()
ax.scatter(X_1[index, 0], P[index], s=50, color="black", label="MPP", zorder=2)
ax.plot(X_1[:, 0], P, color="red", linestyle="--", label="Puissance (µW)", zorder=1)
ax.plot(X_1[:, 0], X_1[:, 1], color="blue", label="Courbe caractéristique")
ax.set_xlabel("Tension (V)")
ax.set_ylabel("Courant (µA)")
ax.legend()
ax.set_title("Courbe caractéristique courant-tension de la cellule photovoltaïque")
fig.show()
fig.savefig("caracteristique_1.pdf")


fig, ax = plt.subplots()
ax.scatter(X_1[:, 0], X_1[:, 1], color="blue", s=10, zorder=1)
ax.scatter(X_2[:, 0], X_2[:, 1], color="orange", s=10, zorder=1)
ax.plot(X_1[:, 0], X_1[:, 1], color="blue", label="Eclairement 1", zorder=1)
ax.plot(X_2[:, 0], X_2[:, 1], color="orange", label="Eclairement 2", zorder=1)
ax.scatter(X_1[0, 0], X_1[0, 1], color="red", s=50, zorder=2)
ax.scatter(X_1[-1, 0], X_1[-1, 1], color="green", s=50, zorder=2)
ax.scatter(X_2[0, 0], X_2[0, 1], color="red", s=50, label="Courant de court-circuit", zorder=2)
ax.scatter(X_2[-1, 0], X_2[-1, 1], color="green", s=50, label="Tension à vide", zorder=2)
ax.set_xlabel("Tension (V)")
ax.set_ylabel("Courant (µA)")
ax.legend()
ax.set_title("Courbes caractéristiques courant-tension de la cellule photovoltaïque")
fig.show()
fig.savefig("caracteristique_2.pdf")


# Réseau de neurones :

# def Q_decalee(u, Qmax, RC, u0):
#     return Qmax * (1 - np.exp((u - u0) / RC))
#
#
# # Calcul de l'erreur quadratique
# def erreur(X, Q_decalee, Qmax, RC, u0):
#     erreur = 0
#     for i in range(len(X)):
#         erreur += (X[i, 1] - Q_decalee(X[i, 0], Qmax, RC, u0))**2
#     return erreur
#
#
# # Gradient de l'erreur par rapport aux paramètres
# def grad_E_i(X, i, Q_decalee, Qmax, RC, u0):
#     u = X[i, 0]
#     temp = (-2 * (X[i, 1] - Qmax*(1 - np.exp((u - u0) / RC))))
#     dQ_dQmax = (1 - np.exp((u - u0) / RC)) * temp
#     dQ_dRC = ((Qmax * np.exp((u - u0) / RC) * (u - u0)) / RC ** 2) * temp
#     dQ_du0 = ((Qmax * np.exp((u - u0) / RC)) / RC) * temp
#
#     return np.array([dQ_dQmax, dQ_dRC, dQ_du0])
#
#
# # Calcul du gradient total de l'erreur
# def grad_E(X, Qmax, RC, u0):
#     return np.sum(np.array([grad_E_i(X, i, Q_decalee, Qmax, RC, u0) for i in range(len(X))]), axis=0)
#
#
# # Descente de gradient
# def descente_gradient(X, Q_decalee, erreur, grad_E, Qmax_0=400, RC_0=1, u0_0=5, lr=0.001, nb_iter=10000):
#     Qmax = [Qmax_0]
#     RC = [RC_0]
#     u0 = [u0_0]
#
#     E = [erreur(X, Q_decalee, Qmax_0, RC_0, u0_0)]
#
#     k = 0
#     while k < nb_iter:
#         k += 1
#
#         print(E[-1])
#
#         Qmax_k, RC_k, u0_k = np.array([Qmax[-1], RC[-1], u0[-1]]) - lr * grad_E(X, Qmax[-1], RC[-1], u0[-1])
#         Qmax.append(Qmax_k)
#         RC.append(RC_k)
#         u0.append(u0_k)
#         e_k = erreur(X, Q_decalee, Qmax_k, RC_k, u0_k)
#         E.append(e_k)
#
#     return Qmax[-1], RC[-1], u0[-1], E[-1]
#
#
# # Affichage de la fonction ajustée
# def display(X, Q_decalee, E, grad_E):
#     Qmax, RC, u0, E = descente_gradient(X, Q_decalee, E, grad_E)
#     print(Qmax, RC, u0, E)
#     # Qmax, RC, u0 = 3, 1, 5
#     u = np.linspace(0, 10, 1000)
#     q = Q_decalee(u, Qmax, RC, u0)
#     fig, ax = plt.subplots()
#     ax.scatter(X[:, 0], X[:, 1])
#     ax.plot(u, q)
#     fig.show()
#
#
# # Lecture des données et affichage du graphique
# X = readData()
# display(X, Q_decalee, erreur, grad_E)