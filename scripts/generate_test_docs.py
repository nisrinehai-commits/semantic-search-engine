"""
Script utilitaire : génère 5 documents .docx réalistes et variés
pour tester la discrimination du moteur de recherche sémantique.
Usage : python scripts/generate_test_docs.py
"""

from pathlib import Path
from docx import Document

OUTPUT_DIR = Path("data/raw")

DOCUMENTS = {
    "doc_peche_durable.docx": """Rapport technique - Pêche durable et gestion des quotas

L'Institut National de Recherche Halieutique mène depuis plusieurs années des études sur
la gestion durable des ressources halieutiques le long des côtes marocaines. Ce rapport
présente les résultats d'un suivi effectué sur les stocks de sardines et d'anchois dans
la zone Atlantique.

Les techniques de pêche durable étudiées incluent la limitation des maillages de filets,
la mise en place de périodes de repos biologique, et l'instauration de quotas annuels par
espèce. Ces mesures visent à préserver le renouvellement naturel des populations de poissons
et à éviter la surexploitation des zones de pêche.

Les données collectées sur les campagnes océanographiques montrent une stabilisation des
stocks depuis la mise en place de ces mesures. Le département recommande la poursuite du
suivi scientifique ainsi qu'un renforcement de la collaboration avec les professionnels du
secteur de la pêche artisanale et industrielle.

Ce travail s'inscrit dans une démarche globale de préservation des ressources marines et de
soutien à une économie de la pêche durable pour les générations futures.""",

    "doc_aquaculture.docx": """Étude sur le développement de l'aquaculture marine

Le développement de l'aquaculture représente un axe stratégique pour diversifier la
production halieutique nationale face à la pression croissante sur les stocks sauvages.
Cette étude évalue le potentiel d'élevage de daurade et de loup de mer dans les fermes
aquacoles situées sur la côte méditerranéenne.

Les paramètres analysés incluent la qualité de l'eau, la densité d'élevage optimale, et
l'impact environnemental des installations sur les écosystèmes marins avoisinants. Les
résultats préliminaires indiquent un taux de croissance satisfaisant des espèces élevées,
avec un impact environnemental maîtrisé lorsque les normes de densité sont respectées.

Le rapport souligne également l'importance de la recherche sur les aliments destinés à
l'aquaculture, afin de réduire la dépendance aux farines de poisson issues de la pêche
sauvage. Des pistes basées sur des sources protéiques alternatives sont actuellement à
l'étude au sein du laboratoire de nutrition aquacole.

Ces travaux contribuent directement aux objectifs de sécurité alimentaire et de
développement durable du secteur de la pêche.""",

    "doc_ressources_humaines.docx": """Note de service - Politique de gestion des ressources humaines

La direction des ressources humaines informe l'ensemble du personnel de la mise à jour de
la politique de télétravail applicable à partir du mois prochain. Les employés pourront
désormais bénéficier de deux jours de télétravail par semaine, sous réserve de validation
par leur responsable hiérarchique.

Cette note rappelle également les modalités de demande de congés annuels, qui doivent être
soumises via la plateforme interne au moins deux semaines avant la date souhaitée. Les
demandes de formation continue peuvent être déposées auprès du service formation tout au
long de l'année.

Un nouveau programme d'intégration pour les nouveaux collaborateurs sera mis en place dès
le trimestre prochain, incluant un parcours d'accueil personnalisé et un système de
mentorat interne. La direction encourage tous les managers à participer activement à ce
programme.

Pour toute question relative à ces dispositions, le service des ressources humaines reste
disponible par email ou sur rendez-vous.""",

    "doc_informatique.docx": """Rapport - Sécurité informatique et infrastructure réseau

Le service informatique a procédé à un audit complet de l'infrastructure réseau de
l'établissement au cours du dernier trimestre. Cet audit a permis d'identifier plusieurs
vulnérabilités liées à des logiciels obsolètes et à une configuration insuffisante des
pare-feux internes.

Des mesures correctives ont été mises en œuvre, notamment la mise à jour de l'ensemble des
postes de travail, le renforcement des politiques de mots de passe, et la mise en place
d'une authentification à deux facteurs pour l'accès aux systèmes sensibles. Une sauvegarde
automatisée quotidienne des serveurs a également été instaurée.

Le rapport recommande la mise en place d'une formation annuelle de sensibilisation à la
cybersécurité pour l'ensemble du personnel, ainsi qu'un renouvellement progressif du parc
informatique vieillissant. Un plan de continuité d'activité en cas d'incident majeur est
actuellement en cours d'élaboration.

Ces actions s'inscrivent dans une démarche de modernisation globale du système
d'information de l'établissement.""",

    "doc_finance.docx": """Rapport budgétaire annuel - Synthèse financière

Ce rapport présente la synthèse de l'exécution budgétaire de l'exercice écoulé. Le budget
total alloué a été exécuté à hauteur de 87 pourcent, avec des écarts notables sur les
postes liés aux équipements scientifiques et aux missions de terrain.

Les dépenses de fonctionnement représentent la part la plus importante du budget, suivies
par les investissements en matériel de laboratoire. Une attention particulière a été portée
à la maîtrise des coûts liés aux déplacements professionnels, en cohérence avec les
directives de rationalisation budgétaire.

Le service financier recommande une meilleure anticipation des besoins en investissement
pour l'exercice suivant, ainsi qu'un suivi trimestriel plus rigoureux de l'exécution
budgétaire par les responsables de service. Un tableau de bord financier actualisé sera mis
à disposition des directions dès le mois prochain.

La prochaine réunion du comité budgétaire est prévue afin de valider les orientations
financières pour l'année à venir.""",
}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, content in DOCUMENTS.items():
        doc = Document()
        for paragraph in content.split("\n\n"):
            doc.add_paragraph(paragraph.strip())
        output_file = OUTPUT_DIR / filename
        doc.save(output_file)
        print(f"[OK] Créé : {output_file}")

    print(f"\n[INFO] {len(DOCUMENTS)} documents générés dans {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()