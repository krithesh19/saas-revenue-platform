import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()
random.seed(42)
np.random.seed(42)

# ─── CONFIG ───────────────────────────────────────────
NUM_CUSTOMERS = 500
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

PLANS = {
    'Starter':    {'mrr': 99,   'weight': 0.40},
    'Growth':     {'mrr': 299,  'weight': 0.30},
    'Business':   {'mrr': 799,  'weight': 0.20},
    'Enterprise': {'mrr': 1999, 'weight': 0.10},
}

SEGMENTS = ['SMB', 'Mid-Market', 'Enterprise']
INDUSTRIES = ['FinTech', 'HealthTech', 'E-Commerce', 'SaaS', 'Logistics', 'EdTech']
CHANNELS = ['Organic', 'Paid Search', 'Referral', 'Partner', 'Outbound']

# ─── CUSTOMERS ────────────────────────────────────────
print("Generating customers...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    segment = random.choices(SEGMENTS, weights=[0.5, 0.35, 0.15])[0]
    signup_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
    customers.append({
        'customer_id': f'CUST{i:04d}',
        'company_name': fake.company(),
        'industry': random.choice(INDUSTRIES),
        'segment': segment,
        'country': random.choices(['Ireland', 'UK', 'USA', 'Germany', 'France'], 
                                   weights=[0.2, 0.25, 0.3, 0.15, 0.1])[0],
        'signup_date': signup_date,
        'acquisition_channel': random.choice(CHANNELS),
        'account_manager': fake.name(),
    })

customers_df = pd.DataFrame(customers)
print(f"  ✓ {len(customers_df)} customers generated")

# ─── SUBSCRIPTIONS ────────────────────────────────────
print("Generating subscriptions...")
subscriptions = []
sub_id = 1

for _, customer in customers_df.iterrows():
    signup_date = pd.to_datetime(customer['signup_date'])
    plan_name = random.choices(list(PLANS.keys()), 
                                weights=[p['weight'] for p in PLANS.values()])[0]
    mrr = PLANS[plan_name]['mrr']
    
    # Add some MRR variation (+/- 10%)
    mrr = round(mrr * random.uniform(0.9, 1.1), 2)
    
    # Churn probability based on segment
    churn_prob = {'SMB': 0.35, 'Mid-Market': 0.20, 'Enterprise': 0.08}[customer['segment']]
    
    is_churned = random.random() < churn_prob
    
    if is_churned:
        min_days = 60
        max_days = (END_DATE - signup_date.to_pydatetime()).days
        if max_days > min_days:
            churn_days = random.randint(min_days, max_days)
            end_date = signup_date + timedelta(days=churn_days)
        else:
            is_churned = False
            end_date = None
    else:
        end_date = None

    # Some customers upgrade plans
    upgraded = not is_churned and random.random() < 0.15
    
    subscriptions.append({
        'subscription_id': f'SUB{sub_id:05d}',
        'customer_id': customer['customer_id'],
        'plan_name': plan_name,
        'mrr': mrr,
        'start_date': signup_date.date(),
        'end_date': end_date.date() if end_date else None,
        'status': 'Churned' if is_churned else 'Active',
        'billing_cycle': random.choices(['Monthly', 'Annual'], weights=[0.6, 0.4])[0],
        'upgraded': upgraded,
        'discount_pct': random.choices([0, 10, 15, 20], weights=[0.7, 0.1, 0.1, 0.1])[0],
    })
    sub_id += 1

subscriptions_df = pd.DataFrame(subscriptions)
print(f"  ✓ {len(subscriptions_df)} subscriptions generated")
print(f"  ✓ Churned: {subscriptions_df[subscriptions_df['status']=='Churned'].shape[0]}")
print(f"  ✓ Active: {subscriptions_df[subscriptions_df['status']=='Active'].shape[0]}")

# ─── INVOICES ─────────────────────────────────────────
print("Generating invoices...")
invoices = []
inv_id = 1

for _, sub in subscriptions_df.iterrows():
    start = pd.to_datetime(sub['start_date'])
    end = pd.to_datetime(sub['end_date']) if sub['end_date'] else pd.to_datetime(END_DATE)
    
    current = start.replace(day=1)
    while current <= end:
        amount = sub['mrr'] * (1 - sub['discount_pct'] / 100)
        
        # Occasional late or failed payments
        payment_status = random.choices(
            ['Paid', 'Paid', 'Paid', 'Late', 'Failed'],
            weights=[0.80, 0.05, 0.05, 0.07, 0.03]
        )[0]
        
        invoices.append({
            'invoice_id': f'INV{inv_id:06d}',
            'subscription_id': sub['subscription_id'],
            'customer_id': sub['customer_id'],
            'invoice_date': current.date(),
            'invoice_month': current.strftime('%Y-%m'),
            'amount_due': round(amount, 2),
            'amount_paid': round(amount, 2) if payment_status != 'Failed' else 0,
            'payment_status': payment_status,
            'plan_name': sub['plan_name'],
        })
        inv_id += 1
        
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

invoices_df = pd.DataFrame(invoices)
print(f"  ✓ {len(invoices_df)} invoices generated")

# ─── SAVE TO CSV ──────────────────────────────────────
os.makedirs('data/raw', exist_ok=True)

customers_df.to_csv('data/raw/customers.csv', index=False)
subscriptions_df.to_csv('data/raw/subscriptions.csv', index=False)
invoices_df.to_csv('data/raw/invoices.csv', index=False)

print("\n✅ All files saved to data/raw/")
print(f"   customers.csv     → {len(customers_df)} rows")
print(f"   subscriptions.csv → {len(subscriptions_df)} rows")
print(f"   invoices.csv      → {len(invoices_df)} rows")