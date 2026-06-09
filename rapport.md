#Projet : Problème d'activation de capteurs pour la surveillance de zones

> **Groupe :** MEYER Timothée / FROEHLY Jean-Baptiste  

---

## 1. Introduction & Formulation Mathématique

Le problème consiste à maximiser la durée de vie d'un réseau de $N$ capteurs sans fil surveillant $M$ zones cibles. Chaque capteur $s_i$ possède une durée de vie (batterie) limitée $T_i$ et surveille un sous-ensemble spécifique de zones. Une **configuration valide** est un sous-ensemble de capteurs dont l'activation simultanée garantit la couverture de toutes les zones cibles. Elle est dite **élémentaire** si aucun capteur de la configuration n'est superflu (c'est-à-dire que le retrait de n'importe quel capteur romprait la couverture complète).

En désignant par $\mathcal{C}$ l'ensemble des configurations élémentaires valides et par $t_c \ge 0$ la durée d'activation de la configuration $c \in \mathcal{C}$, le problème d'ordonnancement optimal se formule sous la forme d'un **programme linéaire (PL)** :

$$
\begin{align*}
\text{Maximiser} \quad & \sum_{c \in \mathcal{C}} t_c \\
\text{sous les contraintes :} \quad & \sum_{c \in \mathcal{C} \text{ t.q. } s_i \in c} t_c \le T_i, \quad \forall i \in \{1, \dots, N\} \\
& t_c \ge 0, \quad \forall c \in \mathcal{C}
\end{align*}
$$

---

## 2. Partie 2 : Construction des Configurations Élémentaires

Étant donné le nombre exponentiel de configurations possibles ($2^N$), nous avons implémenté une **heuristique de recherche tabou** multi-redémarrage afin de générer un pool diversifié de configurations élémentaires valides.

### Algorithme de Recherche Tabou
1. **Initialisation :** Une configuration de départ $S$ est générée aléatoirement en activant chaque capteur avec une probabilité de 30 %.
2. **Fonction de coût :** Pour guider la recherche vers une couverture totale tout en minimisant le nombre de capteurs actifs, nous minimisons la fonction de coût :
   $$f(S) = |S| + \alpha \times \text{zones\_non\_couvertes}(S)$$
   où $\alpha = N + 1$ (pénalité très lourde garantissant qu'une solution valide est toujours préférée à une solution invalide).
3. **Voisinage :** Les voisins d'une solution sont définis par l'inversion d'état d'un seul capteur (actif $\leftrightarrow$ inactif).
4. **Gestion Tabou :** Afin d'éviter les cycles et de sortir des minima locaux, le capteur modifié est placé dans une liste tabou avec une durée de rétention (tenure) de 15 itérations.
5. **Extraction et Minimisation :** Dès qu'une configuration $S$ visitée couvre l'ensemble des cibles, elle est réduite à sa forme **élémentaire** (retrait successif et gourmand de tous les capteurs dont la désactivation ne rompt pas la couverture). Cette configuration épurée est alors ajoutée à un ensemble global de solutions uniques.
6. **Parallélisation et Redémarrages :** L'heuristique est répétée avec 100 redémarrages indépendants lancés en parallèle via un pool de processus (`ProcessPoolExecutor`), assurant une bonne couverture de l'espace des solutions.

---

## 3. Partie 3 : Écriture et Résolution du Programme Linéaire

Une fois le pool de configurations collecté, nous construisons et résolvons le programme linéaire en utilisant la bibliothèque Python **PuLP** avec le solveur **GLPK**.

---

## 4. Partie 4 : Expérimentation et Résultats

Nous avons exécuté notre pipeline d'optimisation sur les 5 instances de test fournies :

| Fichier Instance | Capteurs ($N$) | Zones ($M$) | Configs Générées | Durée de vie optimale ($T^*$) | Temps de calcul |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `0_petit_test.txt` | 4 | 3 | 4 | **8.50** | 0.81 s |
| `1_moyen_test_1.txt` | 20 | 10 | 130 | **104.00** | 0.82 s |
| `1_moyen_test_2.txt` | 10 | 10 | 18 | **395.00** | 0.90 s |
| `2_gros_test.txt` | 100 | 200 | 515 | **1922.17** | 2.01 s |
| `3_maxi_test.txt` | 1000 | 500 | 1947 | **3333.28** | 49.83 s |

### Détail de l'ordonnancement pour `0_petit_test.txt`
Pour l'instance simple à 4 capteurs ($T_1=6, T_2=3, T_3=2, T_4=6$), le solveur active les configurations suivantes :
* **Configuration (2, 4)** active pendant **2.5** unités de temps.
* **Configuration (1, 2)** active pendant **0.5** unités de temps.
* **Configuration (1, 3)** active pendant **2.0** unités de temps.
* **Configuration (1, 4)** active pendant **3.5** unités de temps.
* **Durée de vie totale :** $2.5 + 0.5 + 2.0 + 3.5 = \mathbf{8.5}$ unités de temps.

---

## 5. Partie 5 : Analyse des Résultats

### Influence du nombre de configurations élémentaires
La taille du pool de configurations dépend directement du nombre d'itérations et de redémarrages de la recherche tabou. Nous avons mené une étude de sensibilité sur l'instance `1_moyen_test_1.txt` en faisant varier le nombre de redémarrages (restarts) de l'heuristique :

| Nombre de Redémarrages | Taille du Pool de Configs | Durée de vie optimale ($T^*$) |
| :---: | :---: | :---: |
| 1 | 9 | 54.00 |
| 2 | 27 | 100.00 |
| 5 | 26 | 96.00 |
| 10 | 42 | 104.00 |
| 50 | 100 | 104.00 |
| 100 | 127 | 104.00 |

* **Observation :** Avec un seul démarrage, le pool est restreint et le solveur est fortement bridé (durée de vie de 54.00). Dès que l'on augmente la diversification (plus de restarts), la taille du pool augmente et le solveur trouve de meilleures combinaisons. La convergence vers l'optimum global de **104.00** est atteinte dès 10 redémarrages.

### Influence du type de configurations (Importance de l'Élémentarité)
* **Configurations élémentaires (minimales) :** Elles n'activent que le strict nécessaire pour couvrir la zone. Si une configuration n'est pas élémentaire (par exemple $(1, 2, 3)$ au lieu de $(1, 3)$), le capteur superflu (ici $s_2$) consomme inutilement sa batterie sans apporter de couverture supplémentaire requise. 
* L'application systématique du filtre de minimalisation dans notre recherche tabou est donc cruciale : elle élimine le gaspillage de batterie, réduit le nombre de variables inutiles dans le PL, et garantit que le solveur travaille sur des bases énergétiquement optimales.

