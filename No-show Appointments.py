#!/usr/bin/env python
# coding: utf-8

# # Introduction

# This dataset collects information from 100k medical appointments in Brazil and is focused on the question of whether or not patients show up for their appointment. A number of characteristics about the patient are included in each row.
# 
# ● ‘ScheduledDay’ tells us on what day the patient set up their appointment.
# 
# ● ‘Neighborhood’ indicates the location of the hospital.
# 
# ● ‘Scholarship’ indicates whether or not the patient is enrolled in Brasilian welfare program Bolsa Família.
# 
# ● Be careful about the encoding of the last column: it says ‘No’ if the patient showed up to their appointment, and ‘Yes’ if they did not show up.

# **Kaggle Context**
# 
# Main Question: Why do 30% of patients miss their scheduled appointments?
# 
# 01. PatientId = Identification of a patient
# 02. AppointmentID = Identification of each appointment
# 03. Gender = Male or Female . Female is the greater proportion, woman takes way more care of they health in comparison to man.
# 04. DataMarcacaoConsulta = The day of the actuall appointment, when they have to visit the doctor.
# 05. DataAgendamento = The day someone called or registered the appointment, this is before appointment of course.
# 06. Age = How old is the patient.
# 07. Neighbourhood = Where the appointment takes place.
# 08. Scholarship = True of False . Observation, this is a broad topic, consider reading this article https://en.wikipedia.org/wiki/Bolsa_Fam%C3%ADlia
# 09. Hipertension = True or False
# 10. Diabetes = True or False
# 11. Alcoholism = True or False
# 12. Handcap = True or False
# 13. SMS_received = 1 or more messages sent to the patient.
# 14. No-show = True or False

# In[3]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import sklearn as sk


# In[4]:


df = pd.read_csv('noshowappointments-kagglev2-may-2016.csv')
df.info()


# # Data Wrangling 

# **First off -> We must deal with the date columns format which are: ScheduledDay and AppointmentDay.**

# In[5]:


#Solving Schedule day problem by splitting it into 2 columns
df['Schedule Time'] = pd.to_datetime(df['ScheduledDay'], format='%Y-%m-%d').dt.strftime('%r')
df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')
#Splittign apointmnent time now
df['Appointment Time'] = pd.to_datetime(df['AppointmentDay'], format='%Y-%m-%d').dt.strftime('%r')
df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'], format='%Y-%m-%d').dt.strftime('%Y-%m-%d')

df.info()


# **Now we must do some formatting with the columns labels**

# In[6]:


#Lets put a standard formatting on the column names
df.rename(columns= lambda x: x.lower().replace(' ','_'), inplace=True)
#Now I'll change the no-show columns formatting and values in order to make it less confusing
df.rename(columns={'no-show':'showedup'},inplace=True)
#Lets change the column values to a binary type 0-1
df['showedup'].replace('Yes',' ',inplace=True)
df['showedup'].replace('No','1',inplace=True)
df['showedup'].replace(' ','0',inplace=True)
df['showedup'] = df.showedup.astype('int64')

df.columns


# **Lets continue our formatting**

# In[7]:


#It looks like our appointment_time is always the same so let's remove this column since it wont be any useful
df.appointment_time.unique()
df.drop(columns='appointment_time',inplace=True)


# In[8]:


df.describe()


# It looks like our data has a problem at the column age since the minimum value is -1 and such age is impossible. Now I'll investigate how many rows has this value and determine if we will treat this data or remove it.

# In[9]:


len(df[df['age'] == -1]) #It looks like it's only one row so I'll proceed and remove it

df = df[df['age'] >= 0] #Now we must investigate the rows where the age is 0

#len(df[df['age'] == 0]) #There's 3539 rows with such value!

df[df['age'] == 0].describe()


# I'm a brazilian and I can make an statement that this "Scholarship" it's actually a social welfare programm that provides social and economic benefits for the poor, and therefore it is possible to have people with age 0 on this dataset since it means that they are babies born within a family that is member of this programm. Therefore we will proceed with these rows on the data.

# **Creating a function for our graph modelling**

# In[220]:


def graph(data, y):
    
    x = pd.DataFrame(data.groupby(y).patientid.count()) / data.patientid.count()
    return print('The probability of {}'.format(x.index.names) + 
                 ' {} '.format(x.index[0]) + 
                 'is {}'.format(round(float(x.values[0]),2)) + 
                 ' and the other is {}'.format(round(float(1-x.values[0]),2)))


# # EDA
# 
# Let's break this investigation into parts.
# Firstly let's broadly explore our dataset.
# 
# 01. What's the distribution of age and gender? 
# 02. How many people has been contemplated by the scholarship?
# 03. How many people has any kind of health problem or disability? 
# 04. How many people showed up at their appointments? Did someone make more than one appointment? 

# In[314]:


graf1 = pd.DataFrame(df.groupby(['showedup','gender']).patientid.count())
graf2 = pd.DataFrame(df.groupby(['showedup']).patientid.count())
graf3 = pd.DataFrame(df.groupby('gender').patientid.count())
graf4 = pd.DataFrame(df.groupby('scholarship').patientid.count())
#graf1.plot(kind='scatter', x='showedup', y='patientid')
fig, axes = plt.subplots(nrows=2, ncols=2)

print('The statistics for showedup x gender is ')
print(graf1/graf1.sum())

for x in ['showedup','gender','scholarship']:
    graph(df, x)

graf1.plot(kind='bar', figsize=[12,12], ax=axes[0,0])
graf2.plot(kind='bar', figsize=[12,12], ax=axes[0,1])
graf3.plot(kind='pie', figsize=[12,12], ax=axes[1,0], subplots=True)
graf4.plot(kind='pie', figsize=[12,12], ax=axes[1,1], subplots=True)


# In[364]:


#df.age.plot(kind='hist')
from scipy.stats import norm

sns.distplot(df.age, fit=norm, bins=10)


# It seems like most of our data is represented by Female (~60%). 
# 
# The share of people that showed up on their appointments is ~80% which is composed by 51% of Females and 28% of Males.
# 
# Only ~10% of the people is has a scholarship.
# 
# Our age distribution tends to follow a normal distribution, although it may need some transformations to turn it into a proper normal distribution. It looks like most of the patients are within 20-60 years old, and there's a peak in the 0 years old for a reason.
# 
# Now that we checked the distribution among the profile of our attendee and non-attended, we must check the diseases/malfunctions distribution

# In[315]:


graf1 = pd.DataFrame(df.groupby(['hipertension']).patientid.count())
graf2 = pd.DataFrame(df.groupby(['diabetes']).patientid.count())
graf3 = pd.DataFrame(df.groupby('alcoholism').patientid.count())
graf4 = pd.DataFrame(df.groupby('handcap').patientid.count())

#graf1.plot(kind='scatter', x='showedup', y='patientid')

fig, axes = plt.subplots(nrows=2, ncols=2)

for x in ['hipertension','diabetes','alcoholism','handcap']:
    graph(df,x)

graf1.plot(kind='bar', figsize=[12,12], ax=axes[0,0])
graf2.plot(kind='bar', figsize=[12,12], ax=axes[0,1])
graf3.plot(kind='pie', figsize=[12,12], ax=axes[1,0], subplots=True)
graf4.plot(kind='bar', figsize=[12,12], ax=axes[1,1])


# Most people (~80%) doesnt have hipertension.
# 
# Most people (~90%) doesnt have diabetes
# 
# Most people (~96%) doesnt have alcoholism
# 
# Most people (~97%) are not handcap and among those that are, most has only one handcap (1.8%)

# In[267]:


#How many people had more than one appointment?

print('Share of duplicated appointments: {}'.format(df.patientid.duplicated().sum()/df.patientid.count()))


# Now that we know the share of diseases/malfunctions and demographics of our patients, I guess we should take a look at the profiles that has more than one appointments.

# In[305]:


mask = df.patientid.duplicated()
rep = df.where(mask).dropna().reset_index(drop=True)
rep.describe()


# In[327]:


single = df[~df['patientid'].isin(rep.patientid.values)]
single.describe()


# Looking at the data we have only 37919 people that didn't make more than one appointment, and we have 72607 that made more than one appointment, a total of 110526.
# 
# Looking at the mean of both described tables above doesnt seems like there's much of a difference in most parameters.

# In[376]:


mal = df.copy()
mask = mal[(mal['hipertension'] == 1) |
                     (mal['diabetes'] == 1) |
                     (mal['alcoholism'] == 1) |
                     (mal['handcap'] == 1)].patientid.reset_index(drop=True).copy()

mal[mal.patientid.isin(mask.values)].describe()


# It looks like we have 26303 people with some kind of problem, and their mean age is 58! Much older than the entire dataset mean which is 37.
# 
# It makes sense since the older we get we will unfortunatelly get more diseases

# In[393]:


graf1 = df.groupby(['sms_received','showedup']).patientid.count()

sns.catplot(data=pd.DataFrame((graf1/graf1.sum())).reset_index(), kind='bar', hue='showedup', y='patientid', x='sms_received')


# That's weird! But it looks like most people that went to their appointments didn't receive an SMS, althought most of those that received an SMS also went to their appointments.

# In[407]:


mask = df.copy()
mask.drop(columns=['patientid','appointmentid'], inplace=True)
sns.heatmap(mask.corr())


# The correlation matrix confirms our findings above about hipertension, diabetes and age being positively correlated.

# # Conclusion

# **01. What's the distribution of age and gender?**
# 
# Most people has a mean age of 37 and ~60% of the database is Female. Among those that has any kind of health problem their mean age is 58.
# 
# **02. How many people has been contemplated by the scholarship?**
# 
# Only ~10% of the database has the scholarship
# 
# **03. How many people has any kind of health problem or disability?**
# 
# There are 26303 people with some kind of disability or health problem, most of them are female and their mean age is 58. The most prevalent problems is hipertension and diabetes.
# 
# **04. How many people showed up at their appointments? Did someone make more than one appointment?**
# 
# The share of people that showed up on their appointments is ~80% which is composed by 51% of Females and 28% of Males. Looking at the data we have only 37919 people that didn't make more than one appointment, and we have 72607 that made more than one appointment, a total of 110526.

# # Limitations
# 
# **01. Due to the lesson objective it was used mainly descriptive statistics, and therefore the is no final conclusions, hypothesis or inferences**
# 
# **02. There's a lack of information regarding the appointment system like: what is the SMS policy, what kind of medical specialty session it is, backlog on patient's past behaviors related to diseases. Since this is an analysis regarding sensible medical data, we cannot proceed with a complex analysis without a lot more details regarding the patient and doctor, despite if it is merely for technical demonstration.**
