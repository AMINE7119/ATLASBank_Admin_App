import csv
from datetime import datetime, timedelta
import random

male_first_names = [
   "Mohamed", "Ahmed", "Youssef", "Omar", "Ali", "Hamza", "Ibrahim", "Amine", "Karim", "Hassan", 
   "Mehdi", "Rachid", "Said", "Nabil", "Khalid", "Adil", "Samir", "Hicham", "Younes", "Bilal",
   "Zakaria", "Imad", "Badr", "Ayoub", "Jamal", "Achraf", "Hakim", "Malik", "Tarik", "Soufiane", 
   "Walid", "Mounir", "Marouane", "Yassine", "Fouad", "Abdelali", "Driss", "Mustapha", "Othmane",
   "Brahim", "Ismail", "Redouane", "Abderrahim", "Chakib", "Ilyas", "Aziz", "Abdellah", "Anas",
   "Mohsin", "Abdelaziz", "Yahya", "Oussama", "Jawad", "Abdelhak", "Mostafa", "Elias", "Jalal",
   "Zouhair", "Abderrahman", "Taha", "Abdelkader", "Abdelhadi", "Mohame-Amine", "Adam", "Salim"
]

female_first_names = [
   "Fatima", "Khadija", "Amina", "Zineb", "Laila", "Meryem", "Sara", "Nora", "Aisha", "Hanane",
   "Najat", "Samira", "Karima", "Naima", "Souad", "Ghita", "Houda", "Imane", "Rajae", "Nadia",
   "Salma", "Sanaa", "Jamila", "Loubna", "Rim", "Hafsa", "Siham", "Bouchra", "Asma", "Malika",
   "Hayat", "Oumaima", "Dounia", "Ikram", "Chaima", "Hajar", "Leila", "Fadwa", "Saida", "Wafa",
   "Rachida", "Soukaina", "Safae", "Yasmine", "Ihsane", "Mouna", "Fatima-Zahra", "Jihane", "Hiba",
   "Maha", "Kawtar", "Latifa", "Ibtissam", "Sabrine", "Noura", "Nissrine", "Amal", "Rania", "Farah",
   "Zahra", "Manal", "Lamia", "Samia", "Nabila", "Dalal", "Maria", "Hasna", "Hind", "Fatiha", "Majda"
]

moroccan_last_names = [
   "El Amrani", "Bouhassoun", "Tazi", "Bennis", "Raji", "Alaoui", "Benjelloun", "Idrissi", 
   "Benmoussa", "Fassi", "El Mansouri", "Benali", "Chraibi", "Tahiri", "Lahlou", "Bennani", 
   "El Ouazzani", "Berrada", "Chaoui", "El Khattabi", "El Harrak", "Benkirane", "Ziani",
   "El Hassani", "Lamrani", "Belhaj", "El Kabbaj", "Cherkaoui", "Bekkali", "El Othmani",
   "Sabri", "El Moussaoui", "El Guerrouj", "Bahri", "El Hamdaoui", "Boukricha", "El Jabri",
   "Lazrak", "El Fathi", "Belkadi", "Benslimane", "El Moudden", "Ghazali", "El Badaoui",
   "El Idrissi", "El Fassi", "El Alami", "El Azzouzi", "Belghiti", "El Rhazi", "El Hamdi",
   "Bennasser", "El Mokri", "Belyamani", "El Kadiri", "Benhaddou", "El Filali", "Bouzoubaa",
   "El Omari", "Benchekroun", "El Ghazi", "El Malki", "Bensouda", "El Amiri", "Benzakour"
]

cities_with_districts = {
   "Casablanca": ["Maarif", "Ain Diab", "Bourgogne", "Anfa", "Sidi Belyout", "Hay Hassani", 
                  "Ain Sebaa", "Ben M'Sick", "Sidi Bernoussi", "Al Fida"],
   "Rabat": ["Agdal", "Hassan", "Hay Riad", "Les Orangers", "Youssoufia", "Akkari", 
             "Aviation", "Diour Jamaa", "Médina", "Yacoub El Mansour"],
   "Fes": ["Ville Nouvelle", "Médina", "Saiss", "Atlas", "Agdal", "Zouagha", 
           "Bensouda", "Narjiss", "Route Ain Chkef", "Route Immouzer"],
   "Marrakech": ["Guéliz", "Hivernage", "Médina", "Palmeraie", "Targa", "Massira"],
   "Tanger": ["Malabata", "Marchane", "Médina", "Iberia", "Val Fleuri", "California"],
   "Agadir": ["Talborjt", "Dakhla", "Centre Ville", "Charaf", "Taddart", "Founty"]
}

jobs = [
   "Ingénieur", "Médecin", "Professeur", "Comptable", "Architecte", "Avocat", "Pharmacien",
   "Consultant", "Directeur Commercial", "Chef de Projet", "Analyste Financier", "Développeur",
   "Designer", "Journaliste", "Commercial", "Gestionnaire", "Entrepreneur", "Banquier",
   "Technicien", "Responsable RH", "Enseignant", "Dentiste", "Chef d'Entreprise"
]

def generate_phone():
   return f"+212{random.choice(['6', '7'])}{random.randint(10000000, 99999999)}"

def generate_moroccan_address():
   city = random.choice(list(cities_with_districts.keys()))
   district = random.choice(cities_with_districts[city])
   street_num = random.randint(1, 999)
   return f"{street_num}, Rue {random.randint(1, 100)}, {district}, {city}, Maroc"

def generate_email(first_name, last_name):
   domains = ['gmail.com', 'yahoo.fr', 'hotmail.com', 'outlook.com']
   name = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}"
   return f"{name}@{random.choice(domains)}"

def generate_transaction_description(transaction_type, amount):
   descriptions = {
       'DEPOSIT': [
           'Dépôt de salaire', 'Dépôt en espèces', 'Dépôt par chèque', 'Dépôt mensuel',
           'Versement client', 'Prime annuelle', 'Remboursement', 'Allocation mensuelle'
       ],
       'WITHDRAW': [
           'Retrait au distributeur', 'Retrait en espèces', 'Retrait bancaire',
           'Retrait guichet', 'Paiement carte bancaire', 'Prélèvement mensuel'
       ],
       'TRANSFER': [
           'Paiement de facture', 'Paiement de loyer', 'Virement vers épargne',
           'Virement familial', 'Transfert international', 'Paiement fournisseur',
           'Règlement facture', 'Virement permanent'
       ]
   }
   return f"{random.choice(descriptions[transaction_type])} - {amount} MAD"

def generate_users(num_users=600):
   users = []
   used_emails = set()
   used_phones = set()
   
   for user_id in range(1, num_users + 1):
       gender = random.choice(['M', 'F'])
       first_name = random.choice(male_first_names if gender == 'M' else female_first_names)
       last_name = random.choice(moroccan_last_names)
       
       email = generate_email(first_name, last_name)
       while email in used_emails:
           email = f"{email.split('@')[0]}{random.randint(1, 999)}@{email.split('@')[1]}"
       used_emails.add(email)
       
       phone = generate_phone()
       while phone in used_phones:
           phone = generate_phone()
       used_phones.add(phone)
       
       birth_date = datetime.now() - timedelta(days=random.randint(18*365, 70*365))
       
       users.append({
           'id': user_id,
           'first_name': first_name,
           'last_name': last_name,
           'email': email,
           'phone': phone,
           'address': generate_moroccan_address(),
           'date_of_birth': birth_date.strftime('%Y-%m-%d'),
           'status': True,
           'gender': gender,
           'job': random.choice(jobs),
           'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
       })
   return users

def generate_accounts(users):
   accounts = []
   account_number = 100000
   
   for user in users:
       account_number += 1
       acc_type = random.choice(['savings', 'checking'])
       
       balance = round(random.uniform(0, 100000), 2)
       if random.random() <= 0.05:
           balance = round(random.uniform(100000, 1000000), 2)
       
       accounts.append({
           'number': account_number,
           'user_id': user['id'],
           'type': acc_type,
           'balance': balance,
           'status': True,
           'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
           'interest_rate': round(random.uniform(0.5, 3.5), 2) if acc_type == 'savings' else 0
       })
   return accounts

def generate_transactions(accounts, num_transactions=2000):
   transactions = []
   start_date = datetime.now() - timedelta(days=180)
   
   for _ in range(num_transactions):
       account = random.choice(accounts)
       transaction_type = random.choice(['DEPOSIT', 'WITHDRAW', 'TRANSFER'])
       amount = round(random.uniform(100, 5000), 2)
       
       recipient = None
       if transaction_type == 'TRANSFER':
           recipient = random.choice([a['number'] for a in accounts if a['number'] != account['number']])
       
       transaction_date = start_date + timedelta(
           days=random.randint(0, 180),
           hours=random.randint(0, 23),
           minutes=random.randint(0, 59),
           seconds=random.randint(0, 59)
       )
       
       transactions.append({
           'account_id': account['number'],
           'type': transaction_type,
           'amount': amount,
           'recipient_account': recipient,
           'description': generate_transaction_description(transaction_type, amount),
           'date': transaction_date.strftime('%Y-%m-%d %H:%M:%S')
       })
   
   return sorted(transactions, key=lambda x: x['date'])

def save_to_csv(data, filename, fieldnames):
   with open(filename, 'w', newline='', encoding='utf-8') as file:
       writer = csv.DictWriter(file, fieldnames=fieldnames)
       writer.writeheader()
       writer.writerows(data)

if __name__ == '__main__':
   print("Generating test data...")
   
   users = generate_users(600)
   print(f"Generated {len(users)} users")
   
   accounts = generate_accounts(users)
   print(f"Generated {len(accounts)} accounts")
   
   transactions = generate_transactions(accounts, 2000)
   print(f"Generated {len(transactions)} transactions")
   
   save_to_csv(users, 'users.csv', 
               ['id', 'first_name', 'last_name', 'email', 'phone', 'address', 
                'date_of_birth', 'status', 'gender', 'job', 'created_at'])
   
   save_to_csv(accounts, 'accounts.csv',
               ['number', 'user_id', 'type', 'balance', 'status', 
                'created_at', 'interest_rate'])
   
   save_to_csv(transactions, 'transactions.csv',
               ['account_id', 'type', 'amount', 'recipient_account', 
                'description', 'date'])
   
   print("Data generation completed!")