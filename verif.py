def verifier_configurations(zones_par_capteur: list[list[int]], configurations: list[tuple[int]]) -> None:
    # On déduit toutes les zones que le réseau entier est censé couvrir
    cibles = {z for zones in zones_par_capteur for z in zones}
    print(f"Zones cibles à couvrir : {len(cibles)} zones uniques (ex: {list(cibles)[:5]}).")
    
    print(f"--- DÉBUT DE LA VÉRIFICATION ({len(configurations)} configurations) ---")
    print(f"Objectif : Couvrir {len(cibles)} zones uniques.\n")

    erreurs_trouvees = 0

    for i, config in enumerate(configurations, 1):
        # Attention : tes configurations sont en base 1 (ex: Capteur 22 = index 21)
        config_base_0 = [c - 1 for c in config]
        
        # 1. TEST DE VALIDITÉ (Couverture totale)
        zones_couvertes = set()
        for capteur in config_base_0:
            zones_couvertes.update(zones_par_capteur[capteur])
            
        est_valide = (zones_couvertes == cibles)
        
        if not est_valide:
            zones_manquantes = cibles - zones_couvertes
            print(f"❌ Config {i} {config} INVALIDE : Il manque {len(zones_manquantes)} zones (ex: {list(zones_manquantes)[:5]}).")
            erreurs_trouvees += 1
            continue # Inutile de tester l'élémentarité si ce n'est pas valide
            
        # 2. TEST ÉLÉMENTAIRE (Redondance)
        est_elementaire = True
        capteur_redondant = None
        
        for capteur_a_retirer in config_base_0:
            # On teste la couverture SANS ce capteur
            zones_couvertes_test = set()
            for c in config_base_0:
                if c != capteur_a_retirer:
                    zones_couvertes_test.update(zones_par_capteur[c])
            
            # Si on couvre toujours tout, alors le capteur retiré ne servait à rien !
            if zones_couvertes_test == cibles:
                est_elementaire = False
                capteur_redondant = capteur_a_retirer + 1 # Repassage en base 1 pour l'affichage
                break
                
        if not est_elementaire:
            print(f"⚠️ Config {i} {config} NON ÉLÉMENTAIRE : Le capteur {capteur_redondant} est inutile.")
            erreurs_trouvees += 1
        else:
            print(f"✅ Config {i} {config} PARFAITE (Valide et Élémentaire).")
            pass

    print("\n--- BILAN ---")
    if erreurs_trouvees == 0:
        print("Toutes les configurations sont 100% valides et élémentaires ! Ton heuristique est robuste.")
    else:
        print(f"Attention, {erreurs_trouvees} configuration(s) posent problème.")
