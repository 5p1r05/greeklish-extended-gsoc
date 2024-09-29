import json 

forums_mapping = {'Ειδήσεις':['Νέα', 'NewsPoints', 'Reviews'],
          'Hardware':['Hardware Γενικά', 'Προσφορές', 'Νέα Συστήματα & Αναβαθμίσεις','Επεξεργαστές, Μητρικές & RAM','Kάρτες Γραφικών & \'Hχου', 'Μονάδες Αποθήκευσης', 'Οθόνες', 'Overclocking & Case Modding',
                    'Φορητοί Υπολογιστές', 'Tablets', 'Εκτυπωτές και Πολυμηχανήματα', 'Apple Hardware'],
          'Λειτουργικά Συστήματα':['Windows', 'Linux', 'MacOS'],
          'Software':['Software', 'Mobile Software', 'Video & Audio Software', 'PC Games', 'Console Games'],
          'Διαδίκτυο':['Internet', 'Προγράμματα Fiber, VDSL, ADSL, και κινητής τηλεφωνίας', 'Routers', 'Powerlines, Access Points και Δίκτυα'],
          'Gadgets': ['Gadgets', 'Smartphones', 'Φωτογραφικές Μηχανές & Εξοπλισμός', 'Τηλεoράσεις', 'Home Cinema'],
          'Προγραμματισμός':['Προγραμματισμός', 'Web Design - Development'],
          'Ψυχαγωγία':['Εκπαίδευση & Επαγγ. Προσανατολισμός', 'Κινηματογράφος', 'Τηλεοπτικές Σειρές', 'Mουσική']}

for forum in forums_mapping:
    forum_data = []
    for subforum in forums_mapping[forum]:
        with open(f'subforums_raw/{subforum}.json', 'r') as f:
            data = json.load(f)
            forum_data.extend(data)

    with open(f'forums_raw/{forum}.json', 'w') as f:
        json.dump(forum_data, f, indent=4, ensure_ascii=False)
    