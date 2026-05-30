import pandas as pd
import numpy as np

def calculate_gmv_metrics(df):
    approved = df[df['transaction_status'] == 'Approved']
    total    = len(df)
    gmv      = approved['amount'].sum()
    avg_tx   = approved['amount'].mean() if len(approved) > 0 else 0
    success  = len(approved) / total * 100 if total > 0 else 0
    failed   = df[df['transaction_status'] == 'Failed']
    fail_rt  = len(failed) / total * 100 if total > 0 else 0
    return {
        'gmv':          round(gmv, 2),
        'total_tx':     total,
        'approved_tx':  len(approved),
        'avg_tx_value': round(avg_tx, 2),
        'success_rate': round(success, 1),
        'failure_rate': round(fail_rt, 1)
    }

def daily_gmv_trend(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    approved   = df[df['transaction_status'] == 'Approved']
    daily      = approved.groupby('date').agg(
        gmv=('amount', 'sum'),
        transactions=('transaction_id', 'count')
    ).reset_index()
    daily['date']        = pd.to_datetime(daily['date'])
    daily['daily_growth'] = daily['gmv'].pct_change() * 100
    return daily

def payment_method_analysis(df):
    approved = df[df['transaction_status'] == 'Approved']
    method   = df.groupby('payment_method').agg(
        total=('transaction_id', 'count'),
        approved=('transaction_status',
                  lambda x: (x == 'Approved').sum()),
        revenue=('amount',
                 lambda x: x[df.loc[x.index,
                 'transaction_status'] == 'Approved'].sum()
                 if len(x) > 0 else 0)
    ).reset_index()
    method['success_rate'] = \
        method['approved'] / method['total'] * 100
    return method

def failure_analysis(df):
    failed = df[df['transaction_status'] == 'Failed']
    if len(failed) == 0:
        return pd.DataFrame()
    reasons = failed['failure_reason'].value_counts().reset_index()
    reasons.columns = ['Reason', 'Count']
    reasons['Percentage'] = \
        reasons['Count'] / len(failed) * 100
    return reasons

def city_performance(df):
    city = df.groupby('city').agg(
        total_tx=('transaction_id', 'count'),
        gmv=('amount',
             lambda x: x[df.loc[x.index,
             'transaction_status'] == 'Approved'].sum()),
        failed=('transaction_status',
                lambda x: (x == 'Failed').sum())
    ).reset_index()
    city['failure_rate'] = \
        city['failed'] / city['total_tx'] * 100
    return city.sort_values('gmv', ascending=False)

def customer_analytics(df):
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    last_date = df['timestamp'].max()
    cust = df.groupby('customer_id').agg(
        total_tx=('transaction_id', 'count'),
        total_spent=('amount', 'sum'),
        last_tx=('timestamp', 'max'),
        approved=('transaction_status',
                  lambda x: (x == 'Approved').sum())
    ).reset_index()
    cust['days_since_last'] = \
        (last_date - cust['last_tx']).dt.days
    cust['churn_risk'] = cust['days_since_last'].apply(
        lambda x: '🔴 High'   if x > 60
             else '🟡 Medium' if x > 30
             else '🟢 Active'
    )
    cust['success_rate'] = \
        cust['approved'] / cust['total_tx'] * 100
    return cust