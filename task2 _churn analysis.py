import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# trying to use glob to find where the files are unzipped inside my dowloads folder, since I don't know the exact path 
# This prevents path errors if the files are inside a subfolder
search_pattern = os.path.join("C:\\Users\\david\\Downloads","**","ravenstack_*.csv")
found_files = glob.glob(search_pattern,recursive=True)

# Dictionary to hold dataframes
ans = {}
for path in found_files:
    name = os.path.basename(path).replace('.csv', '')
    ans[name] = pd.read_csv(path)

# Extracting tables into normal variables
accounts = ans['ravenstack_accounts']
tickets = ans['ravenstack_support_tickets']
churn_events = ans['ravenstack_churn_events']

print("Files loaded successfully.")

# --- Part 1: Baseline Churn ---
total_accounts = len(accounts)
churned_accounts = accounts['churn_flag'].sum()
overall_churn_rate = (churned_accounts / total_accounts) * 100

print("baseline stats")
print("Total Accounts:", total_accounts)
print("Total Churned:", churned_accounts)
print(f"Overall Churn Rate: {overall_churn_rate:.2f}%")



print("churn by industry")
# Group by industry to see where churn is the highest
industry_churn = accounts.groupby('industry')['churn_flag'].agg(['count', 'sum'])
industry_churn['churn_rate_%'] = (industry_churn['sum'] / industry_churn['count']) * 100
print(industry_churn.sort_values(by='churn_rate_%', ascending=False))


 #Churn Reasons 
print("reason codes for churned accounts")
# Counting the reason codes from the churn events file
reason_counts = churn_events['reason_code'].value_counts()
reason_pct = churn_events['reason_code'].value_counts(normalize=True) * 100

for reason in reason_counts.index:
    print(f"- {reason}: {reason_counts[reason]} accounts ({reason_pct[reason]:.1f}%)")


# Support Ticket Analysis ---
print("SUPPORT METRICS FOR CHURNED VS ACTIVE ACCOUNTS ")
# Merge the datasets together using account_id
ticket_churn_analysis = pd.merge(tickets, accounts[['account_id', 'churn_flag']], on='account_id', how='left')

# Calculating means for support metrics
support_metrics = ticket_churn_analysis.groupby('churn_flag')[['resolution_time_hours', 'satisfaction_score', 'first_response_time_minutes']].mean()
print(support_metrics)

print("Escalation Rates")
escalation_rates = ticket_churn_analysis.groupby('churn_flag')['escalation_flag'].mean() * 100
print(escalation_rates)


#  Plotting the Chart ---
print("Plotting the industry churn chart")
plt.figure(figsize=(8, 5))

# Sorting values first so the graph looks neat
plot_data = industry_churn.reset_index().sort_values(by='churn_rate_%', ascending=False)

# Simple barplot
ax = sns.barplot(x='industry', y='churn_rate_%', data=plot_data, color='skyblue')

# Setting up labels and titles
plt.title('RavenStack Account Churn Rate by Industry')
plt.xlabel('Industry')
plt.ylabel('Churn Rate (%)')
plt.ylim(0, 40)

# Putting the percentage text numbers on top of the bars
for p in ax.patches:
    ax.annotate(f"{p.get_height():.1f}%", 
                (p.get_x() + p.get_width() / 2., p.get_height() + 0.5), 
                ha='center', va='bottom')

plt.tight_layout()

# Saving the file to the project folder
plt.savefig('industry_churn_rates.png')
print("Chart saved as industry_churn_rates.png")