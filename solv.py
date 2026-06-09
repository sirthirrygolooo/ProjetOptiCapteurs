import pulp

def resoudre_ordonnancement(n_capteurs: int, duree_de_vie_capteurs: list[int], configurations: list[tuple[int]]) -> tuple[float, list[tuple[tuple[int], float]]]:
    prob = pulp.LpProblem("Maximisation_Duree_Vie_Reseau", pulp.LpMaximize)

    temps_activation = pulp.LpVariable.dicts(
        "Temps_Config", 
        range(len(configurations)), 
        lowBound=0, 
        cat=pulp.LpContinuous
    )

    prob += pulp.lpSum([temps_activation[c] for c in range(len(configurations))])

    for capteur in range(n_capteurs):
        prob += pulp.lpSum([
            temps_activation[c] 
            for c, config in enumerate(configurations) 
            if capteur in config
        ]) <= duree_de_vie_capteurs[capteur]

    prob.solve(pulp.GLPK_CMD(msg=False))

    resultats_configurations = []
    for c in range(len(configurations)):
        valeur = temps_activation[c].varValue
        if valeur is not None and valeur > 0:
            resultats_configurations.append((configurations[c], valeur))

    duree_totale = pulp.value(prob.objective)

    return duree_totale, resultats_configurations

def afficher_solution(duree_totale: float, resultats_configurations: list[tuple[tuple[int], float]]) -> None:
    print(f"Durée de vie optimale du réseau : {duree_totale}")
    print("Détail de l'activation des configurations :")
    for config, temps in resultats_configurations:
        print(f"  - Configuration {config} activée pendant {temps} unités de temps")
