-- Admins table
CREATE TABLE admins (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password TEXT NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO admins (username, password, email, role) 
VALUES ('admin', 'admin123', 'admin@bank.com', 'ADMIN');
VALUES ('amine', '069151', 'amine@bank.com', 'SUPERADMIN');
INSERT INTO admins (username, password, email, role) 
VALUES ('amine', '069151', 'amine@bank.com', 'SUPERADMIN');
-- USERS
CREATE TABLE users (
   id SERIAL PRIMARY KEY,
   first_name VARCHAR(50) NOT NULL,
   last_name VARCHAR(50) NOT NULL,
   email VARCHAR(255) UNIQUE NOT NULL,
   phone VARCHAR(20) UNIQUE NOT NULL,
   address VARCHAR(255) NOT NULL,
   date_of_birth DATE NOT NULL,
   status BOOLEAN DEFAULT true,
   gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Accounts
CREATE TABLE accounts (
  number SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('savings', 'checking')),
  balance DECIMAL(10,2) DEFAULT 0,
  status BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT one_account_type_per_user UNIQUE (user_id, type)
);

-- Transactions
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY, 
  account_id INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL CHECK (type IN ('DEPOSIT', 'WITHDRAW', 'TRANSFER')),
  amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
  recipient_account INTEGER,
  description TEXT,
  date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(number) ON DELETE CASCADE,
  FOREIGN KEY (recipient_account) REFERENCES accounts(number) ON DELETE SET NULL,
  CONSTRAINT valid_transfer CHECK (
      (type = 'TRANSFER' AND recipient_account IS NOT NULL) OR 
      (type IN ('DEPOSIT', 'WITHDRAW') AND recipient_account IS NULL)
  )
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_accounts_user ON accounts(user_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_recipient ON transactions(recipient_account);
CREATE INDEX idx_transactions_date ON transactions(date);


-- ALTER TABLE
ALTER TABLE users ADD COLUMN job VARCHAR(100);
ALTER TABLE accounts ADD COLUMN interest_rate DECIMAL(5,2);